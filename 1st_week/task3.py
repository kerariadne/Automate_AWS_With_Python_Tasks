data = {
    1: [
        { "seat_name": "a1", "isTaken": True },
        { "seat_name": "a2", "isTaken": False },
        { "seat_name": "a3", "isTaken": True },
        { "seat_name": "a4", "isTaken": True },
        { "seat_name": "a5", "isTaken": False },
    ],
    2: [
        { "seat_name": "b1", "isTaken": True },
        { "seat_name": "b2", "isTaken": True },
        { "seat_name": "b3", "isTaken": True },
        { "seat_name": "b4", "isTaken": True },
        { "seat_name": "b5", "isTaken": True },
    ],
    3: [
        { "seat_name": "c1", "isTaken": False },
        { "seat_name": "c2", "isTaken": True },
        { "seat_name": "c3", "isTaken": True },
        { "seat_name": "c4", "isTaken": True },
        { "seat_name": "c5", "isTaken": False },
    ],
}

print('შეიყვანეთ ვაგონის ნომერი: ')
train_number = int(input())
print('შეიყვანეთ ადგილის ნომერი: ')
seat_number = int(input())

if data[train_number][seat_number-1]["isTaken"] == True:
    print('ადგილი დაკავებულია')
    for i in data[train_number]:
        if i["isTaken"] == False:
            print(f'უახლოესი თავისუფალი ადგილია {i["seat_name"]}; ადგილის ნომერი: {data[train_number].index(i)+1}')
            break
    else:
        print('ყველა ადგილი დაკავებულია ამ ვაგონში, მოვძებნით სხვა ვაგონში')
    
    for i in data:
        for j in reversed(data[i]):
            if j["isTaken"] == False:
                print(f'უახლოესი თავისუფალი ადგილია {j["seat_name"]}; ადგილის ნომერი: {data[i].index(j)+1} ვაგონის ნომერი: {i}')
                break
        else:
            continue
        break
else:
    print('ადგილი ხელმისაწვდომია')