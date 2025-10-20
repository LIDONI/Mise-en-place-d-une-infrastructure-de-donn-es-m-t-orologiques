import pandas as pd
import json
import boto3
import os
from dotenv import load_dotenv
import io
from pymongo import MongoClient

# -------------------------------
# CONFIGURATION
# -------------------------------
load_dotenv()

AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION_NAME = os.getenv("AWS_REGION", "eu-west-3")

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "Meteo_data_db")

# -------------------------------
# S3 CLIENT
# -------------------------------
def get_s3_client():
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=REGION_NAME
        )
        return s3
    except Exception as e:
        print(f"Erreur création client S3 : {e}")
        return None

# -------------------------------
# Lecture S3
# -------------------------------
def smart_read_csv(bucket, key, nrows=None):
    s3 = get_s3_client()
    if not s3:
        return pd.DataFrame()

    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        raw_bytes = obj["Body"].read()
    except Exception as e:
        print(f"Erreur get_object {bucket}/{key} : {e}")
        return pd.DataFrame()

    # Airbyte
    try:
        df = pd.read_csv(io.BytesIO(raw_bytes), usecols=["_airbyte_data"], nrows=nrows, low_memory=False)
        df["_airbyte_data"] = df["_airbyte_data"].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
        return pd.json_normalize(df["_airbyte_data"])
    except Exception:
        pass

    # CSV standard
    for sep in [",", ";", "\t"]:
        try:
            df = pd.read_csv(io.BytesIO(raw_bytes), sep=sep, nrows=nrows, low_memory=False)
            if not df.empty:
                return df
        except Exception:
            continue

    print(f"Impossible de parser {key}")
    return pd.DataFrame()

# -------------------------------
# MongoDB
# -------------------------------
def get_mongo_client():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("Connexion à MongoDB réussie.")
        return client
    except Exception as e:
        print(f"Erreur de connexion MongoDB : {e}")
        return None

def insert_dataframe_to_mongodb(df, collection_name, db_name=MONGO_DATABASE):
    client = get_mongo_client()
    if not client:
        print("Connexion MongoDB impossible, insertion annulée.")
        return

    try:
        db = client[db_name]
        collection = db[collection_name]
        records = df.to_dict("records")
        if records:
            result = collection.insert_many(records, ordered=False)
            print(f"{len(result.inserted_ids)} documents insérés dans '{collection_name}'.")
        else:
            print(f"DataFrame vide pour '{collection_name}', aucun document inséré.")
    except Exception as e:
        print(f"Erreur insertion MongoDB : {e}")
    finally:
        client.close()

# -------------------------------
# Migration principale
# -------------------------------
files = [
    "Data_JSON/Donnees_JSON/2025_09_21_1758483200407_0.csv",
    "Data_JSON/Google_drive_Ichtegem/2025_09_23_1758670114136_0.csv",
    "Data_JSON/Google_drive_Madeleine/2025_09_23_1758668827948_0.csv"
]

for f in files:
    collection_name = f.split('/')[1].replace('_', '').replace('.', '').lower()
    print(f"\n=== Traitement {f} -> {collection_name} ===")
    
    df = smart_read_csv(AWS_S3_BUCKET, f)
    if df.empty:
        print(f"Le fichier {f} est vide ou mal formaté. Ignoré.")
        continue

    df_clean = df.dropna()
    if df_clean.empty:
        print(f"Toutes les lignes contiennent des valeurs manquantes pour {collection_name}. Ignoré.")
        continue
    else:
        print(f"{len(df) - len(df_clean)} lignes supprimées pour valeurs manquantes.")

    insert_dataframe_to_mongodb(df_clean, collection_name)

# -------------------------------
# Contrôle qualité
# -------------------------------
def check_data_quality(bucket, key, collection_name):
    df_source = smart_read_csv(bucket, key)
    client = get_mongo_client()
    if not client:
        return
    db = client[MONGO_DATABASE]
    df_target = pd.DataFrame(list(db[collection_name].find({}, {"_id":0})))
    client.close()

    print(f"\n=== Contrôle qualité {collection_name} ===")
    print(f"Source : {len(df_source)} lignes | MongoDB : {len(df_target)} documents")
    print(f"Colonnes identiques : {set(df_source.columns) == set(df_target.columns)}")
    if not df_target.empty:
        missing_ratio = df_target.isnull().sum() / len(df_target)
        print("Taux de valeurs manquantes (%) :")
        print((missing_ratio*100).round(2))

for f in files:
    collection_name = f.split('/')[1].replace('_', '').replace('.', '').lower()
    check_data_quality(AWS_S3_BUCKET, f, collection_name)
