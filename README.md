# FerryboxData Code challenge
## Usage
###### Install
```
docker-compose build
docker-compose up -d
```
The explanations and comments are added throughout the python,  dockerfile, docker-compose file

###### Testing the code
Run the following command
```
docker-compose run ferrycode 
```
This will trigger the python script from docker and wait for user input.

## Input Output Data
###### Input data
**Input data** in the [folder](code/env_ferrybox/data/all_json/)

###### output folder
Output **Map and chart** in the [folder](code/env_ferrybox/data/map/) <br/>
Output **merge csv file** in the [folder](code/env_ferrybox/data/csv/) <br/>
## Methodology
All the action below automatically take care by the script

1. The JSON dataset is stored in a list of array.
2. The dataset is reduced and removed the unwanted fields. 
3.	All the data points falling outside the area of map interest are removed
![image](https://user-images.githubusercontent.com/10088434/165376904-9cd983f5-e115-41dd-9c47-f66b8a7bc2ef.png)
![image](https://user-images.githubusercontent.com/10088434/165377654-9fff543c-77da-4c1c-a3bf-ec301cfb24b6.png)


4.	All the points where pump value 0 is removed.
5.	Visually interpretate the data under line chart and box plot
![image](https://user-images.githubusercontent.com/10088434/165377512-c1bed828-c0ec-4983-a316-876e0e39619f.png)
![image](https://user-images.githubusercontent.com/10088434/165377566-d71467db-eb20-49f2-8e47-67706bbfa28f.png)

7.	Identifying outliers with the 1.5xIQR rule.
8.	Finally, map is classified into outliers and non-outliers values for both Inlet temperature and CTD temperature. <br/><br/>
Inlet temparature <br/>
![image](https://user-images.githubusercontent.com/10088434/165377946-25c722cc-b7f1-4afc-9cbc-ca3ec6e89eea.png)
 
CTD temparature <br/>
![image](https://user-images.githubusercontent.com/10088434/165378193-b26d8154-00be-4ea6-a42a-86d2702c117a.png)



