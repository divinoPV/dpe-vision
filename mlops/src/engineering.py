import polars as pl

(
    pl.read_csv("./../data/train.csv", infer_schema_length=10000)
    .group_by(["Type_bâtiment", "Code_INSEE_(BAN)", "Etiquette_DPE"])
    .agg(
        [
            pl.col("Etiquette_DPE").count().alias("sum_dpe"),
            pl.col("Surface_habitable_logement").mean().alias("mean_surface_livable"),
            pl.col("Conso_5_usages/m²_é_finale").mean().alias("mean_consumption_m2")
        ]
    )
).write_parquet("./../data/cleaned/cleaned.parquet")
