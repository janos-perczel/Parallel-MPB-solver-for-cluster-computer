
import numpy as np
# import matplotlib.pyplot as plt



tot_no_bands = 4

off_set = 2
# band_n0 = 37
no_of_pos = 10
x_int_no = 100
z_int_no = 100
tot_int_pos = x_int_no * z_int_no

regular_band_data = ''
plot_index_data = ''
line_counter = 0
with open("data_all.dat") as infile:
	for line in infile:
		list_of_entries = line.split(',')
		# print len(list_of_entries)
		# print type(list_of_entries[1])
		# print list_of_entries[-1] == '\n'

		line_counter += 1

		if not line_counter%4 == 1:
			continue


		for band_no in range(tot_no_bands):

			#write regular datainto separate file:
			band_index = band_no + 1
			if band_index == 1:
				regular_band_data += ','.join(str(x) for x in list_of_entries[0:3])+','
			reg_start_index = 1 + 2 + (band_index-1) *((1+3*no_of_pos) + tot_int_pos)
			reg_end_index = 1 + 2 + (band_index-1) *((1+3*no_of_pos) + tot_int_pos) + (1+3*no_of_pos)
			regular_line = ','.join(str(x) for x in list_of_entries[reg_start_index:reg_end_index])
			regular_band_data += regular_line
			regular_band_data += ','

			# #write intensity data into file:
			# if line_counter > 1:
			# 	int_start_index = 1 + 2 + (band_index-1) *((1+3*no_of_pos) + tot_int_pos) + (1+3*no_of_pos)
			# 	int_end_index = 1 + 2 + (band_index-1) *((1+3*no_of_pos) + tot_int_pos) + (1+3*no_of_pos) + tot_int_pos 
			# 	int_data = map(float,list_of_entries[int_start_index:int_end_index])
			# 	print len(int_data)
			# 	int_matrix = np.array(int_data).reshape((z_int_no, x_int_no))
			# 	top_region = np.sum(int_matrix[0:33,:])
			# 	middle_region = np.sum(int_matrix[33:66,:])
			# 	bottom_region = np.sum(int_matrix[66:,:])
			# 	if middle_region > (top_region + bottom_region):
			# 		plot_index = 1
			# 	else:
			# 		plot_index = 0
			# 	plot_index_data += str(plot_index) 
			# 	plot_index_data += ','

		print('Parsing line %i...'%line_counter)


			# if band_no == 17 and line_counter == 2:
			# 	im = plt.imshow(int_matrix)
			# 	plt.colorbar(im)
			# 	plt.show()
				

		regular_band_data += '\n'
		plot_index_data += '\n'

# print plot_index_data
# print regular_band_data

with open('reg_data.dat', 'w') as file:
	file.write(regular_band_data) 

# with open('plot_index_data.dat', 'w') as file:
# 	file.write(plot_index_data) 

