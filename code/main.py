import pathlib
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from shapely.geometry import Point, Polygon
import folium
import webbrowser


#Define Global variable
sensor_file_path=[] # Array of json file url
dataTable=[] # Array of data after removing unwanted fileds
dataTableGeo=[] # Array of data after removing out side the map extent
df_pumpStatus_filter = None # Array of data after removing outlier
root_path = pathlib.Path(__file__).parent.resolve() # Workspace of the main script
data_source_directory= pathlib.Path.joinpath(root_path, 'env_ferrybox/data/all_json') # Directory containig list of jsons

## the main function execute the entire process
def toolbox():

    try:
        ######################### data preparation and cleaning#########################

        ##loop through all the json file
        for path in pathlib.Path(data_source_directory).iterdir():
            sensor_file_path.append(path)
        count = 0

        ##extract the required filed from the json and store to the array
        for filePath in sensor_file_path:
            df_org = pd.read_json(filePath)
            for node in df_org.t:
                #print(node)
                dataTable.append({'slNo': count,

                                   'signal_id':node['properties']['signal_id'],
                                  'platform_code' : node['properties']['platform_code'],
                                  'datetime': node['properties']['datetime'],

                                  'pumpStatus': node['measurements']['FA/ferrybox/SYSTEM/PUMP'],
                                  'inletTemp': node['measurements']['FA/ferrybox/INLET/TEMPERATURE'],
                                  'ctdTemp': node['measurements']['FA/ferrybox/CTD/TEMPERATURE'],

                                  'longitude': node['location']['FA/gpstrack']['longitude'],
                                  'latitude': node['location']['FA/gpstrack']['latitude']


                                  })
                count += 1
        print('Total json file found {0}'.format(count))




        ## define the bounding box/map extent of the given data
        coords = [(6.20838,51.8041), (6.20838, 62.1548), (15.3098,62.1548), (15.3098, 51.8041 )]
        poly = Polygon(coords)



        ## Add all location on the map to see the geographic distribution
        map_folium=folium.Map(location=[poly.centroid.y,poly.centroid.x],zoom_start=4 )
        folium.GeoJson(poly, name='Data Spatial Extent').add_to(map_folium)
        output_map_filePath = pathlib.Path.joinpath(root_path, r'env_ferrybox/data/map/mapAll.html')
        ferryLayerAll = folium.FeatureGroup(name="Signal Location").add_to(map_folium)
        for obj in dataTable:
            folium.Circle(
                radius=100,
                location=[obj['latitude'],obj['longitude']],
                popup=obj['signal_id'],
                color="#00ABFD",
                fill=True,
                #icon=folium.Icon(icon="cloud"),
            ).add_to(ferryLayerAll)

        folium.LayerControl().add_to(map_folium)
        map_folium.save(output_map_filePath)
        webbrowser.open(output_map_filePath)



        ## Remove all the points out side the map extent
        for obj in dataTable:
            point = Point(obj['longitude'],obj['latitude'])
            if(point.within(poly)):
                dataTableGeo.append(obj)

        ## Remove all the data where pump is off
        df_pumpStatus_filter = pd.DataFrame.from_dict(dataTableGeo)
        df_pumpStatus_filter = df_pumpStatus_filter.loc[df_pumpStatus_filter['pumpStatus'] > 0]


        ## Store the data as csv file as a given location
        output_csv_filePath_filter = pathlib.Path.joinpath(root_path, 'env_ferrybox/data/csv/filterData.csv')
        df_pumpStatus_filter.to_csv(output_csv_filePath_filter,index=False)
        print('\n\nTotal row after data cleaning {0}'.format(len(df_pumpStatus_filter.index)))

        ######################### End of data preparation and cleaning #########################



        ######################### visual interpretation of outlier  #########################


        # Disply the anomaly/outlier in the line chart
        figLine = go.Figure()
        figLine.add_trace(go.Scatter(y=df_pumpStatus_filter['inletTemp'],
                                 mode='lines',
                                 name='inletTemp'))
        figLine.add_trace(go.Scatter(y=df_pumpStatus_filter['ctdTemp'],
                                 mode='lines',
                                 name='ctdTemp'))
        figLine.update_layout(
            title="Line chart spike as a anomalies",
            xaxis_title="Record ID",
            yaxis_title="Temp <sup>O</sup>C",
            legend_title="Inputs",

        )

        ## store the line chart disaply as html file in the give location
        figLine.write_html(pathlib.Path.joinpath(root_path, "env_ferrybox/data/map/figLine.html"))
        webbrowser.open_new_tab(pathlib.Path.joinpath(root_path, "env_ferrybox/data/map/figLine.html"))


        ## Disply the anomaly/outlier in the whisker box plot
        figBoxp = go.Figure()
        figBoxp.add_trace(go.Box(x=df_pumpStatus_filter['inletTemp'], name='Inlet Temp',),)
        figBoxp.add_trace(go.Box(x=df_pumpStatus_filter['ctdTemp'], name='CTD Temp',))
        figBoxp.update_layout(
            title="Box Plot Diagram to Identify Outliers",
            yaxis_title="",
            xaxis_title="Temp <sup>O</sup>C",
            legend_title="Inputs",

        )

        ## store the boxplot disaply as html file in the give location
        figBoxp.write_html( pathlib.Path.joinpath(root_path,"env_ferrybox/data/map/figBoxp.html"))
        webbrowser.open_new_tab(pathlib.Path.joinpath(root_path, "env_ferrybox/data/map/figBoxp.html"))

        ######################### End of visual interpretation of outlier  #########################



        ######################### Detect the outliers uisng the 1.5xIQR rule  #########################

        ## Detect and display outlier from inlet temp
        print("\n \n")
        print("############### Statistics from inlet Temp data ################")
        print(IQR_outlier_formula(df_pumpStatus_filter['inletTemp'])['stat'])
        print('List of all outlier inlet Temp data')
        print(IQR_outlier_formula(df_pumpStatus_filter['inletTemp'])['outliers'])
        print('Total outliers:' + str(len(IQR_outlier_formula(df_pumpStatus_filter['inletTemp'])['outliers'])))

        ## Detect and display outlier  from ctc temp
        print("\n \n")
        print("############### Statistics from inlet CTD data ################")
        print(IQR_outlier_formula(df_pumpStatus_filter['ctdTemp'])['stat'])
        print('List of all outlier CTD Temp data')
        print(IQR_outlier_formula(df_pumpStatus_filter['ctdTemp'])['outliers'])
        print( 'Total outliers:'+str(len(IQR_outlier_formula(df_pumpStatus_filter['ctdTemp'])['outliers']) ))


        ############ Create a classify map to show outlier and non outlier  #################
        map_folium_final=folium.Map(location=[poly.centroid.y,poly.centroid.x],
                              zoom_start=6,
                              )
        output_finalmap_filePath = pathlib.Path.joinpath(root_path, 'env_ferrybox/data/map/mapFinal.html')

        ferryLayerFilterInletTepm = folium.FeatureGroup(name="Signal Inlet Temp").add_to(map_folium_final)
        ferryLayerFilterCTDTepm = folium.FeatureGroup(name="Signal CTD Temp").add_to(map_folium_final)

        # loop though the final dataset and use the IQR to classify the points
        for index, row in df_pumpStatus_filter.iterrows():

            if(detect_outlier(df_pumpStatus_filter['inletTemp'],row['inletTemp'])):
                folium.Circle(
                    radius=150,
                    location=[row['latitude'],row['longitude']],
                    popup=str(row['inletTemp']) + '<sup>o</sup>C',
                    color="red",
                    fill=True,
                    #icon=folium.Icon(icon="cloud"),
                ).add_to(ferryLayerFilterInletTepm)
            else:
                folium.Circle(
                    radius=150,
                    location=[row['latitude'],row['longitude']],
                    popup=str(row['inletTemp']) + '<sup>o</sup>C',
                    color="green",
                    fill=True,
                    #icon=folium.Icon(icon="cloud"),
                ).add_to(ferryLayerFilterInletTepm)

            if(detect_outlier(df_pumpStatus_filter['ctdTemp'],row['ctdTemp'])):
                folium.Circle(
                    radius=150,
                    location=[row['latitude'],row['longitude']],
                    popup=str(row['ctdTemp']) + '<sup>o</sup>C',
                    color="red",
                    fill=True,
                    #icon=folium.Icon(icon="cloud"),
                ).add_to(ferryLayerFilterCTDTepm)
            else:
                folium.Circle(
                    radius=150,
                    location=[row['latitude'],row['longitude']],
                    popup=str(row['ctdTemp']) + '<sup>o</sup>C',
                    color="#00ABFD",
                    fill=True,
                    #icon=folium.Icon(icon="cloud"),
                ).add_to(ferryLayerFilterCTDTepm)
        folium.LayerControl().add_to(map_folium_final)
        map_folium_final.save(output_finalmap_filePath)
        webbrowser.open(output_finalmap_filePath)

######################### End Detect the outliers uisng the 1.5xIQR rule  #########################


######################### Intractive outliers finder function tigger  #########################
        detect_outlier_based_on_inputs(df_pumpStatus_filter)
######################### End Intractive outliers finder function tigger  #########################

        print('End of the process')

    except Exception as e:
        print(e)



##function to calulate dataset Outliers usng 1.5IQR rule and return the as a list
def IQR_outlier_formula(dataSet):
    q1, q3 = np.percentile(sorted(dataSet), [25, 75])

    iqr_intelTemp = q3 - q1

    lower_bound_intelTemp = q1 - (1.5 * iqr_intelTemp)
    upper_bound_intelTemp = q3 + (1.5 * iqr_intelTemp)

    outliers_val = [x for x in dataSet if
                x <= lower_bound_intelTemp or x >= upper_bound_intelTemp]

    dataStat= dataSet.describe()

    return {'outliers': outliers_val,'stat':dataStat, 'lower_bound': lower_bound_intelTemp,'upper_bound' : upper_bound_intelTemp }



##function to calulate single input usng 1.5IQR rule and return Outliers as true false
def detect_outlier(dataset,val):
    boundInfo = IQR_outlier_formula(dataset)
    if(val <= boundInfo['lower_bound'] or val >= boundInfo['upper_bound']):
        return True
    else:
        return False


##function to create a intractive session and resposne to outlier based on user input in the console section
def detect_outlier_based_on_inputs(df_pumpStatus_filter):
    print("\n \n Please select the folowing number : \n 1.INLET TEMPERATURE \n 2.CTD TEMPERATURE \n 3.Reset \n 4.Exit \n")
    userVal = int(input("Please provide input: \n"))

    match userVal:
        case 1:
            print("You have selected a INLET TEMPERATURE option for finding anomalies")
            val = float(input("Please provide value for INLET TEMPERATURE : \n"))
            outresult= detect_outlier(df_pumpStatus_filter['inletTemp'], val)
            if outresult:
                print('Its a outliers :( \n \n')
            else:
                print('Its not outliers :) \n \n')


            userTry = int(input("Want to try another number: \n 1.Yes \n 2.No \n"))
            if userTry ==1:
                detect_outlier_based_on_inputs(df_pumpStatus_filter)
            else:
                exit()

        case 2:
            print("You have selected a CTD TEMPERATURE option for finding anomalies")
            val = float(input("Please provide value for CTD TEMPERATURE : \n"))
            outresult= detect_outlier(df_pumpStatus_filter['ctdTemp'], val)

            if outresult:
                print('Its a outliers :( \n \n')
            else:
                print('Its not outliers :) \n \n')

            userTry = int(input("Want to try another number: \n 1. Yes \n 2 . No \n"))
            if userTry == 1:
                detect_outlier_based_on_inputs(df_pumpStatus_filter)
            else:
                exit()

        case 3:
            detect_outlier_based_on_inputs(df_pumpStatus_filter)

        case 4:
            exit()

        case _:
            print("Something went wrong! or Not a valid input")
            detect_outlier_based_on_inputs(df_pumpStatus_filter)


if __name__ == '__main__':
    toolbox()