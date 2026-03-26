INSERT INTO STORE (StoreID, StoreName, Phone, StoreEmail, Rating)

SELECT
    store_num AS StoreID,

    'Rami Levy ' ||
    areas[((store_num - 1) / 10) + 1] ||
    ' Branch ' || ((store_num - 1) % 10 + 1)
    AS StoreName,

    '05-' || LPAD((1000000 + store_num)::text, 7, '0')
    AS Phone,

    'store' || store_num || '@ramilevy.co.il'
    AS StoreEmail,

    (1 + (store_num % 10)) AS Rating  

FROM generate_series(1, 500) AS store_num,
(
    SELECT ARRAY[
        'Tel Aviv','Jerusalem','Haifa','Rishon LeZion','Petah Tikva',
        'Ashdod','Netanya','Beer Sheva','Holon','Bnei Brak',
        'Rehovot','Ashkelon','Bat Yam','Herzliya','Kfar Saba',
        'Hadera','Modiin','Nazareth','Lod','Ramla',
        'Afula','Eilat','Tiberias','Kiryat Gat','Yavne',
        'Nahariya','Raanana','Givatayim','Kiryat Ono','Rosh HaAyin',
        'Yokneam','Zichron Yaakov','Caesarea','Pardes Hanna','Or Akiva',
        'Karmiel','Safed','Migdal HaEmek','Nof HaGalil','Kiryat Shmona',
        'Dimona','Arad','Mevaseret Zion','Maale Adumim','Beit Shemesh',
        'Nes Ziona','Shoham','Gedera','Gan Yavne','Kiryat Malakhi'
    ] AS areas
) a;