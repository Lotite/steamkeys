from pyspark.sql import SparkSession, functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, LongType
import os

# Levantamos la sesión de Spark y el context para que todo rule
spark = SparkSession.builder \
    .appName("SteamPriceProcessor") \
    .getOrCreate()

sc = spark.sparkContext

# Definimos el schema para los datos oficiales de Steam
# Queremos que los tipos de datos sean exactos desde el principio
game_schema = StructType([
    StructField("steam_id", LongType(), True),
    StructField("name", StringType(), True)
])

# Cargamos el master de juegos oficiales de Steam

official_games = spark.read.schema(game_schema).json("/user/hadoop/steam/games/") \
    .select(F.col("steam_id").alias("meta_id"), F.col("name").alias("official_name"))

# Pillamos los datos crudos del scraping
scraped_keys = spark.read.json("/user/hadoop/steam/scrapin/") \
    .withColumnRenamed("name", "store_name")

# Esta función limpia los nombres para que el match sea mucho más fácil
def clean_and_prep(columna):
    # Palabras que meten ruido en las tiendas de keys
    noise_terms = "steam|digital|xbox|live|key|pc|global|europe|edition|standard|deluxe|premium|gift|row|mac|linux"
    content_tags = "dlc|expansion|pass|pack|content"
    
    clean_text = F.lower(columna)
    clean_text = F.regexp_replace(clean_text, r"\(.*?\)|\[.*?\]", "") # Fuera basura entre paréntesis
    clean_text = F.regexp_replace(clean_text, noise_terms + "|" + content_tags, "") # Limpiamos los tags de tienda
    clean_text = F.regexp_replace(clean_text, r"[^a-z0-9]", "") # Nos quedamos solo con lo básico para evitar líos
    return F.trim(clean_text)

# Preparamos el dataset oficial para el join
df_master_clean = official_games.withColumn("is_dlc_meta", F.lower(F.col("official_name")).rlike("dlc|expansion|pass|pack")) \
    .withColumn("match_key", clean_and_prep(F.col("official_name"))) \
    .filter(F.col("match_key") != "")

# Preparamos los datos del scraping para el cruce
df_keys_clean = scraped_keys.withColumn("is_dlc_key", F.lower(F.col("store_name")).rlike("dlc|expansion|pass|pack")) \
    .withColumn("match_key", clean_and_prep(F.col("store_name")))

# Hacemos el inner join para cruzar ambos mundos
# Usamos broadcast join porque el master de juegos suele ser más pequeño
merged_df = df_keys_clean.join(
    F.broadcast(df_master_clean),
    (df_keys_clean.match_key == df_master_clean.match_key) & 
    (df_keys_clean.is_dlc_key == df_master_clean.is_dlc_meta),
    "inner"
)

# Si hay registros repetidos: nos quedamos con el más nuevo
# Creamos una Window function agrupada por meta_id
sort_window = Window.partitionBy("meta_id").orderBy(F.col("register_time").desc())
final_dedup_df = merged_df.withColumn("ranking", F.row_number().over(sort_window)) \
    .filter(F.col("ranking") == 1)

# Pillamos las columnas que nos interesan para el resultado final
# Queremos mantener la info original pero con el nombre oficial de Steam
store_cols = [c for c in scraped_keys.columns if c not in ["store_name", "state"]]

output_df = final_dedup_df.select(
    F.col("official_name").alias("name"), 
    *store_cols,
    F.col("meta_id").alias("steam_id"),
    F.lit(1).alias("state")
)

# Guardamos el resultado procesado en HDFS
target_path = "/user/hadoop/steam/steamkey"

output_df.write.mode("overwrite").json(target_path)

# Un pequeño print para ver que todo ha ido bien
print(f"Hemos sacado {output_df.count()} juegos asociados.")
output_df.show(5, False)

# Si queremos limpiar la carpeta de entrada al terminar
# os.system("hdfs dfs -rm -r /user/hadoop/steam/scrapin/*")
