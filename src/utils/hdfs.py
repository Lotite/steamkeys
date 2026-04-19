import pandas as pd
import requests
import json

def obtener_dataframe_hdfs(subcarpeta, limite=200):
    base_url = f"http://hadooplotfi.duckdns.org:9870/webhdfs/v1/user/hadoop/steam/{subcarpeta}"
    user = "hadoop"
    
    try:
        r_list = requests.get(f"{base_url}?op=LISTSTATUS", timeout=20)
        r_list.raise_for_status()
        archivos = r_list.json()['FileStatuses']['FileStatus']
        
        registros_encontrados = []
        contador = 0
        
        for f in archivos:
            if f['type'] == 'FILE' and contador < limite:
                nombre_fichero = f['pathSuffix']
                url_lectura = f"{base_url}/{nombre_fichero}?op=OPEN&user.name={user}"
                
                try:
                    respuesta = requests.get(url_lectura, allow_redirects=True, timeout=10)
                    
                    lineas = respuesta.text.strip().split('\n')
                    for linea in lineas:
                        if linea.strip():
                            registros_encontrados.append(json.loads(linea))
                    
                    contador += 1
                except:
                    continue
        
        if not registros_encontrados:
            return pd.DataFrame({"Aviso": [f"No se pudieron leer datos de {subcarpeta}"]})
            
        return pd.DataFrame(registros_encontrados)

    except Exception as e:
        return pd.DataFrame({"Error": [f"Error en {subcarpeta}: {str(e)}"]})

if __name__ == "__main__":
    dataset = obtener_dataframe_hdfs("games", limite=1000)
    dataset.to_csv("games.csv")
    print(dataset)