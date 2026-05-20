import database.my_crud_lib as db

def main():
    db.create_table()

    db.insert_user('Alice', 30)
    db.insert_user('Bob', 25)
    db.insert_user('Charlie', 35)

    print('사용자 조회')
    users = db.get_users()
    for user in users:
        print(user)
    
    db.update_user('Alice', 40)
    db.update_user('Bob', 33)

    print('두번째 조회')
    user = db.get_user_by_name('Alice')
    print(user)

    db.delete_user_by_name('Alice')

    print('세번째 조회')
    users = db.get_users()
    for user in users:
        print(user)

if __name__ == '__main__':
    main()
