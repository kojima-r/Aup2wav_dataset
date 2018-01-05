python3 ./make_dataset_split.py ./original_data/*.aup
sh ./convert_split.sh > convert_split.log
python3 ./postprocess_split.py ./original_data/*.aup
