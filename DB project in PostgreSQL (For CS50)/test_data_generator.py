import random
from datetime import datetime, timedelta

airlines = {1: 'US', 2: 'GB', 3: 'CN', 4: 'US',
            5: 'US', 6: 'RU', 7: 'FR', 8: 'US'}


def aircraft(ac_number):
    unique_sn = []
    registration_nums = []
    query_lines = []
    for i in range(ac_number):

        sn = random.randint(10000, 99999)
        while sn in unique_sn:  # Needed to exclude duplicates
            sn = random.randint(10000, 99999)
        unique_sn.append(sn)

        airline_id = random.randint(1, 8)

        country = airlines[airline_id]
        reg_num = str(random.randint(1000, 9999))
        registration = f'{country}-{reg_num}'
        while registration in registration_nums:
            reg_num = str(random.randint(1000, 9999))
            registration = f'{country}-{reg_num}'
        registration_nums.append(registration)

        ac_type = random.choice(('B737', 'A320'))
        amp_id = 1 if ac_type == 'B737' else 2  # Choose maintenance program depanding on a/c type
        FC = random.randint(0, 9999)
        next_check_FC = random.randint(FC, FC+400)
        FH = random.randint(FC, FC*5)  # FC - to make FH no less
        next_check_FH = random.randint(FH, FH+3000)
        query_lines.append(f"('SN{sn}', '{registration}', {airline_id}, '{ac_type}', "
          f"{FC}, {next_check_FC}, {FH}, {next_check_FH}, {amp_id})")
    return query_lines

def random_date(start_date, end_date):
    # Calculate the difference in days between the start and end dates
    delta = end_date - start_date
    # Generate a random number of days to add to the start_date
    random_days = random.randint(0, delta.days)
    # Return the new date as a formatted string
    return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")


def engines(nums):
    unique_esn = []
    query_lines = []
    ac_id = 1
    eng_types = ('CFM56-3', 'CFM56-5', 'CFM56-7')
    eng = random.choice(eng_types)
    for i in range(nums):
        esn = random.randint(10000, 99999)
        while esn in unique_esn:
            esn = random.randint(10000, 99999)
        unique_esn.append(esn)
        airline_id = random.randint(1, 8)
        if i != 0 and i % 2 == 0:
            ac_id = ac_id + 1
            saved_id = ac_id
            eng = random.choice(eng_types)
        else:
            saved_id = ac_id
        ac_id = random.choices(('NULL', ac_id), weights=[1, 99], k=1)[0]
        FC = random.randint(0, 9999)
        overhaul_FC = random.choice((random.randint(0, FC), 'NULL'))
        if overhaul_FC != 'NULL':
            overhaul_date = f"'{random_date(start_date, end_date)}'"
        else:
            overhaul_date = 'NULL'
        if ac_id != 'NULL':
            status = 'installed'
        else:
            status = random.choice(('storage', 'overhaul'))
        query_lines.append(f"('ESN{esn}', {airline_id}, {ac_id}, "
                           f"'{eng}', {FC}, {overhaul_FC}, "
                           f"{overhaul_date}, '{status}')")
        ac_id = saved_id
    return query_lines


def records(number):
    record_lines = []
    for i in range(number):
        for j in range(random.randint(1, 20)):
            check_id = random.randint(1, 2)
            date = random_date(start_date, end_date)
            FC_record = random.randint(100, 1000)
            FH_record = random.randint(500, 10000)
            record_lines.append(f"({i+1}, {check_id}, '{date}', {FC_record}, "
                  f"{FH_record})")
    return record_lines


# Define the start and end date range
start_date = datetime(1990, 1, 1)  # Start date
end_date = datetime(2024, 1, 1)  # End date


with open("test_data_2test.sql", "w", encoding="utf-8") as f:
    f.write('INSERT INTO "aircraft" ("ac_serial_number", "reg_num", '
            '"airline_id", "ac_type", "ac_flight_cycles", '
            '"next_check_fc", "ac_flight_hours", "next_check_fh", '
            '"amp_id")\nVALUES\n')
    ac_lines = aircraft(100)
    for i, line in enumerate(ac_lines):
        f.write(line)
        if i < len(ac_lines) - 1:
            f.write(",\n")
        else:
            f.write("\n")
    f.write(';\n\n')
    f.write('INSERT INTO "engines" ("eng_serial_number", "airline_id", '
            '"ac_id", "eng_type", "eng_flight_cycles", "last_overhaul_fc", '
            '"last_overhaul_date", "eng_status")\nVALUES\n')
    eng_lines = engines(100)
    for i, line in enumerate(eng_lines):
        f.write(line)
        if i < len(eng_lines) - 1:
            f.write(",\n")
        else:
            f.write("\n")
    f.write(';\n\n')
    f.write('INSERT INTO maintenance_records (ac_id, check_id, '
            'date_completion, "fc_record", "fh_record")\nVALUES\n')
    rc_lines = records(50)
    for i, line in enumerate(rc_lines):
        f.write(line)
        if i < len(rc_lines) - 1:
            f.write(",\n")
        else:
            f.write("\n")
    f.write(';\n')
