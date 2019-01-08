import os
import csv
import xlsxwriter
import numpy

def function(file):
    if file.endswith('.csv'): # add year before ".csv" to get information for that specific year
        f = open(file, "r")
        reader = csv.reader(f)
        margins = []
        difference_in_margins = []
        team = file.split('.csv')[0]
        ahead = 0
        behind = 0
        tied = 0
        average_margin = 0
        stdev = 0
        total_free_throws = 0
        late_free_throws = 0
        diff_results = 0
        header = reader.__next__()
        for row in reader:
            margin = int(row[2]) - int(row[1])
            final = int(row[4]) - int(row[3])
            if margin > 0 and final < 0:
                diff_results += 1
            elif margin < 0 and final > 0:
                diff_results += 1
            diff_in_margin = margin - final
            difference_in_margins.append(diff_in_margin)
            total_free_throws += int(row[5])
            late_free_throws += int(row[6])
            if margin > 0:
                ahead += 1
            elif margin < 0:
                behind += 1
            else:
                tied += 1
            margins.append(margin)
            
        margins = numpy.array(margins)
        if len(margins) > 0:
            average_margin = numpy.mean(margins)
            stdev = numpy.std(margins)
        else:
            average_margin = 0
            stdev = 0
        sheet.write_string(index, 0, team)
        sheet.write_number(index, 1, ahead)
        sheet.write_number(index, 2, behind)
        sheet.write_number(index, 3, tied)
        if numpy.isnan(average_margin) == False:
            sheet.write_number(index, 4, average_margin)
            sheet.write_number(index, 5, stdev)
        else:
            sheet.write_number(index, 4, 0)
            sheet.write_number(index, 5, 0)  
        sheet.write_number(index, 6, sum(difference_in_margins))
        try:
            sheet.write_number(index, 7, float((late_free_throws/total_free_throws)*100))
        except ZeroDivisionError:
            sheet.write_number(index, 7, 0)
        sheet.write_number(index, 8, diff_results)
        f.close()

writer = xlsxwriter.Workbook('Aggregate.xlsx')
sheet = writer.add_worksheet()
sheet.write_string('A1', 'Team')
sheet.write_string('B1', 'Ahead')
sheet.write_string('C1', 'Behind')
sheet.write_string('D1', 'Tied')
sheet.write_string('E1', 'Average Margin')
sheet.write_string('F1', 'Standard Deviation')
sheet.write_string('G1', 'Change in Margin Over Last 2 Minutes')
sheet.write_string('H1', 'Percentage of Free Throws in Last 2 Minutes')
sheet.write_string('I1', 'Different Results')

directory = os.path.join("c://","/Users/samthomas/Desktop/two-minute-score-project")
index = 1
for file in os.listdir(directory):
    function(file)
    index += 1
writer.close()

    
            