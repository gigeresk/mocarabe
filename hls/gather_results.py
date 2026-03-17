import csv


def get_data(file_name):
    count = len(open(file_name).readlines())
    if count == 22:
        first_line = 4
        second_line = 18
        latency_line = 11
    else:
        first_line = 3
        second_line = 17
        latency_line = 10
    with open(file_name) as fp:
        for i, line in enumerate(fp):
            if i == first_line:
                a = line.split(",")
                unroll = a[1].strip()
                lut = a[2].strip()
                ff = a[3].strip()
                dsp = a[4].strip()
                freq = a[6].strip()
                if freq == "":
                    freq = "0"
                else:
                    freq = "{:.2f}".format(1000 * 1 / float(freq))
            elif i == second_line:
                a = line.split("|")
                acheived_ii = a[5].strip()
            elif i == latency_line:
                a = line.split("|")
                latency_min = a[1].strip()
                latency_max = a[2].strip()
    return unroll, lut, ff, dsp, freq, acheived_ii, latency_min, latency_max


# print(get_data("iic3.txt"))
csv_in = open("iiunrolls.csv", "r")
# csv_out = open('hls_no_constraint_results.csv', 'w')
csv_out = open("hls_results.csv", "w")

writer = csv.writer(csv_out, delimiter=",")
writer.writerow(
    [
        "name",
        "unroll_factor",
        "target_ii",
        "achieved_ii",
        "adder",
        "multiplier",
        "lut_usage",
        "ff_usage",
        "dsp_usage",
        "achieved_frequency",
        "latency_min",
        "latency_max",
    ]
)
j = 0
for row in csv.reader(csv_in):
    # print(row[1])
    if j == 0:
        j += 1
        continue
    bench_name = row[0]
    ii = row[1]
    # name = "./"+bench_name+"/iic"+ii+".txt"
    name = "./" + bench_name + "/ii" + ii + ".txt"
    try:
        j += 1
        unroll, lut, ff, dsp, freq, acheived_ii, latency_min, latency_max = get_data(
            name
        )
        # print(unroll, lut, ff, dsp, freq, acheived_ii,name)
        adder = row[2]
        multi = row[3]
        unroll = row[4]
        writer.writerow(
            [
                bench_name[4:],
                unroll,
                ii,
                acheived_ii,
                adder,
                multi,
                lut,
                ff,
                dsp,
                freq,
                latency_min,
                latency_max,
            ]
        )
    except Exception as e:
        print(e)
csv_out.close()
