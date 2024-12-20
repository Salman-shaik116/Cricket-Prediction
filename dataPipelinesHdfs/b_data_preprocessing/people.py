"""Module for processing player information from T20 cricket matches."""

import os
import sys
import logging
import pandas as pd
import utils

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
import config

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_players_data():
    """
    Process player information from match data files.

    This function reads player information from match info files, processes them
    to create two datasets:
    1. match_players - containing player participation in each match
    2. players - containing unique player records with their team information

    Returns:
        None
    """
    try:
        # Initialize HDFS client
        client = utils.get_hdfs_client()
        hdfs_data_path = config.HDFS_BASE_DIR

        # Check the contents of the directory on HDFS
        logging.info(f'Checking contents of HDFS directory: {os.path.join(hdfs_data_path, "1_rawData", "t20s_csv2")}')
        dir_contents = utils.hdfs_list(client, os.path.join(hdfs_data_path, '1_rawData', 't20s_csv2'))

        # Find all CSV files in the specified directory
        info_files = [f for f in dir_contents if f.endswith('_info.csv')]
        logging.info(f'Found {len(info_files)} info files.')

        if len(info_files) == 0:
            logging.warning(f'No info files found in {os.path.join(hdfs_data_path, "1_rawData", "t20s_csv2")}. Please check the directory and file permissions.')

        dataframes = pd.DataFrame(columns=['country', 'player', 'player_id', 'season', 'match_id'])
        injured_matches = []

        for info_file in info_files:
            match_id = pd.to_numeric(info_file.split('/')[-1].split('_')[0])
            try:
                with utils.hdfs_read(client, os.path.join(hdfs_data_path, '1_rawData', 't20s_csv2', info_file)) as reader:
                    df = pd.read_csv(reader, header=None, names=['type', 'heading', 'subkey', 'players', 'player_id'], skipinitialspace=True).drop('type', axis=1)
                players_df = df[df['heading'] == "player"].drop(['heading', 'player_id'], axis=1)
                registry_df = df[df['heading'] == "registry"].drop('heading', axis=1)
                merged_df = players_df.merge(registry_df[['players', 'player_id']], on='players', how='inner')
                merged_df.rename(columns={'players': 'player', 'subkey': 'country'}, inplace=True)
                season = df['subkey'][5]
                merged_df['match_id'] = match_id
                merged_df['season'] = season
                if len(merged_df) != 22:
                    raise Exception('Injured Match')
                dataframes = pd.concat([dataframes, merged_df])
            except Exception:
                injured_matches.append(match_id)

        logging.info(f'Processed all files. Injured matches: {injured_matches}')

        # Save dataframes to HDFS
        try:
            with utils.hdfs_write(client, f'{hdfs_data_path}/2_processedData/match_players', encoding='utf-8', overwrite=True) as writer:
                dataframes.to_csv(writer, index=False)
            logging.info('Saved match_players.csv to HDFS.')
        except Exception as e:
            logging.error(f'Error saving match_players to HDFS: {e}')
            raise

        # Individual player's data
        players = dataframes.drop('match_id', axis=1).drop_duplicates(subset=['player', 'country', 'player_id'])

        # Save players to HDFS
        try:
            with utils.hdfs_write(client, f'{hdfs_data_path}/2_processedData/players.csv', encoding='utf-8', overwrite=True) as writer:
                players.to_csv(writer, index=False)
            logging.info('Saved players.csv to HDFS.')
        except Exception as e:
            logging.error(f'Error saving players.csv to HDFS: {e}')
            raise

    except Exception as e:
        logging.critical(f'Critical error: {e}')
        raise
    return

if __name__ == "__main__":
    process_players_data()