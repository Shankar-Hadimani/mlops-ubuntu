import requests

from tqdm import tqdm

files = [("green_tripdata_2022-01.parquet", "."), ("green_tripdata_2021-01.parquet", "./evidently_service/datasets")]

print("Downloading files")
for file, path in files:
    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{file}"
    save_path = f'{path}/{file}'
    response = requests.get(url=url, stream=True)
    with open(save_path, "wb") as file_in:
        for data in tqdm(
            response.iter_content(),
            desc=f'{file}',
            postfix=f' being saved to {save_path}',
            total=int(response.headers["Content-Length"])):

            file_in.write(data)


