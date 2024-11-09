
import os
import logging
from player_stats.spark_utils import create_spark_session, load_data, save_data
from player_stats.preprocessing import preprocess_batting_data, preprocess_bowling_data, preprocess_fielding_data, map_country_codes

def preprocess_batting():
    logging.info("Starting preprocess_batting task.")
    spark = create_spark_session()
    base_dir = "hdfs://192.168.245.142:8020/usr/ravi/t20"
    raw_data_dir = os.path.join(base_dir, 'data', '1_rawData')
    processed_data_dir = os.path.join(base_dir, 'data', '2_processedData')

    country_codes = {
        # ...existing country codes...
    }

    try:
        batting_data = load_data(spark, raw_data_dir, 't20_batting_stats.csv')
        batting_data = preprocess_batting_data(batting_data)
        batting_data = map_country_codes(batting_data, country_codes)
        save_data(batting_data, processed_data_dir, 'batting_data.csv')
        logging.info("Batting data processing and saving completed successfully.")
    except Exception as e:
        logging.error(f"Error in preprocess_batting task: {e}")
        raise
    finally:
        spark.stop()
        logging.info("Spark session stopped.")

def preprocess_bowling():
    logging.info("Starting preprocess_bowling task.")
    spark = create_spark_session()
    base_dir = "hdfs://192.168.245.142:8020/usr/ravi/t20"
    raw_data_dir = os.path.join(base_dir, 'data', '1_rawData')
    processed_data_dir = os.path.join(base_dir, 'data', '2_processedData')

    country_codes = {
        # ...existing country codes...
    }

    try:
        bowling_data = load_data(spark, raw_data_dir, 't20_bowling_stats.csv')
        bowling_data = preprocess_bowling_data(bowling_data)
        bowling_data = map_country_codes(bowling_data, country_codes)
        save_data(bowling_data, processed_data_dir, 'bowling_data.csv')
        logging.info("Bowling data processing and saving completed successfully.")
    except Exception as e:
        logging.error(f"Error in preprocess_bowling task: {e}")
        raise
    finally:
        spark.stop()
        logging.info("Spark session stopped.")

def preprocess_fielding():
    logging.info("Starting preprocess_fielding task.")
    spark = create_spark_session()
    base_dir = "hdfs://192.168.245.142:8020/usr/ravi/t20"
    raw_data_dir = os.path.join(base_dir, 'data', '1_rawData')
    processed_data_dir = os.path.join(base_dir, 'data', '2_processedData')

    country_codes = {
        # ...existing country codes...
    }

    try:
        fielding_data = load_data(spark, raw_data_dir, 't20_fielding_stats.csv')
        fielding_data = preprocess_fielding_data(fielding_data)
        fielding_data = map_country_codes(fielding_data, country_codes)
        save_data(fielding_data, processed_data_dir, 'fielding_data.csv')
        logging.info("Fielding data processing and saving completed successfully.")
    except Exception as e:
        logging.error(f"Error in preprocess_fielding task: {e}")
        raise
    finally:
        spark.stop()
        logging.info("Spark session stopped.")

def combine_data():
    logging.info("Starting combine_data task.")
    spark = create_spark_session()
    processed_data_dir = "hdfs://192.168.245.142:8020/usr/ravi/t20/data/2_processedData"

    try:
        batting_data = load_data(spark, processed_data_dir, 'batting_data.csv')
        bowling_data = load_data(spark, processed_data_dir, 'bowling_data.csv')
        fielding_data = load_data(spark, processed_data_dir, 'fielding_data.csv')
        players_data = load_players_data(spark, processed_data_dir)

        batting_data = batting_data.join(players_data, ['Player', 'Country'], 'inner')
        bowling_data = bowling_data.join(players_data, ['Player', 'Country'], 'inner')
        fielding_data = fielding_data.join(players_data, ['Player', 'Country'], 'inner')

        bowling_data = bowling_data.drop('Mat', 'Inns')
        fielding_data = fielding_data.drop('Mat', 'Inns')

        player_data = batting_data.join(
            bowling_data, on=['player_id', 'Player', 'Country', 'Season'], how='inner'
        ).join(
            fielding_data, on=['player_id', 'Player', 'Country', 'Season'], how='inner'
        ).drop('Cumulative Mat', 'Cumulative Inns')

        save_data(player_data, processed_data_dir, 'playerstats.csv')
        logging.info("Data combining and saving completed successfully.")
    except Exception as e:
        logging.error(f"Error in combine_data task: {e}")
        raise
    finally:
        spark.stop()
        logging.info("Spark session stopped.")