#written: Aug 8, 2017

import os, sys, subprocess, pickle, re, time, math, random
#from popen2 import popen2
import numpy as np

#use script for "run" or "fetch"
mode = sys.argv[1]

#PICK GEOMETRY:
# diamond:1 , slab+diamond:2 , rods+diamond:3 , holes+diamond:4, diamond+dents:5, slab+holes:6, slab+holes+inf diamond:7
geo_variable = 8

function_name = 'master.ctl' #name of the MPB master file

# root directory for creating temporary directories to store output
dirroot = os.getcwd()

######### Parameters ##########
#number of bands:
no_of_bands = 4
#permittivity of PC rods
eps = 3.25**2
#permittivity of diamond
diamond = 2.4**2


#hole spacing
hole_spacing = 1/3.
#distort
distort_factor = 1.2

#height of supercell
supercell_h = 4
#number of lattice cells
lattice_width = 1
#height of rods
h_rods_array = 1.5 * hole_spacing
#height of diamond
h_diamond_array = 0.5
#radius of rods
r_array = 0.25 * hole_spacing
r_distort = 0.35 * hole_spacing
# #field samling location loc
# field_loc = np.array([0,0,0],dtype=float)
#sample only a single k point?
single_point = 1 #choose one if parallelized.
#no of k points to interpolate between Gamma,K and X:
k_interp_no = 28
total_k_points = 3 * k_interp_no + 4 


for k_index in range(total_k_points):

	h_rods = h_rods_array
	h_diamond = h_diamond_array
	r = r_array

	dirroot = os.getcwd()

	current_name = '%0.2fr%0.2fd%0.2fr_k%i'%(h_rods,h_diamond,r,k_index+1)

	folder_name = 'folder_%s'%(current_name)

	this_dir = dirroot+ "//" + folder_name

	if mode=="run":

		# create a temporary directory to hold the script and output
		os.mkdir(this_dir)


		os.chdir(this_dir)

		# print "entered folder %s"%current_name

		command1 = "cp ../*.m ."
		proc = subprocess.Popen(command1,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)                   
		proc.wait()

		params = {'h_rods':h_rods,'h_diamond': h_diamond,'r':r,'current_name':current_name,'single_point':single_point,'k_index':k_index+1,'geo_variable':geo_variable,'no_of_bands':no_of_bands,'supercell_h':supercell_h,'eps':eps,'diamond':diamond,'k_interp':k_interp_no,'lattice_width':lattice_width,'hole_spacing':hole_spacing,'distort_factor':distort_factor,'r_distort':r_distort}

		slurm_script="""#!/bin/bash
#
#SBATCH --mail-type=FAIL,END # when to send email?
#SBATCH --mail-user=perczelj@gmail.com
#SBATCH -p serial_requeue,general
#SBATCH -n 1
#SBATCH -N 1
#SBATCH --mem 2500
#SBATCH -t 0-10:00
#SBATCH -o f_%(current_name)s.out
#SBATCH -e f_%(current_name)s.err

module load gcc/7.1.0-fasrc01 mpb/1.6.1-fasrc02

mpb $1 >& $2 """%params

		slurm_name = "a12_%0.2f_%0.2f_%s"%(distort_factor,r_distort,current_name)
		# write the script file
		f = open(this_dir + "//%s.sh"%slurm_name,"w")
		f.write(slurm_script)
		f.close()


###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################
		mpb_script = """;diamond slab with triangular lattice of rods on top 

(define-param h-diamond %(h_diamond)0.2f) ; the thickness of the diamond slab
(define-param h-rods %(h_rods)0.2f) ; the thickness of the PC rods
(define-param eps %(eps)0.4f) ; the dielectric constant of the slab
(define-param diamond %(diamond)0.4f)
(define-param r %(r)0.2f) ; the radius of the rods
(define-param r-distort %(r_distort)0.2f)
(define-param supercell-h %(supercell_h)0.2f) ; height of the supercell
(define-param lattice-width %(lattice_width)i) ; number of lattice cells
(define-param no-of-bands %(no_of_bands)i) ; no of bands to calculate
(define single-point %(single_point)i)

(define-param hole-spacing %(hole_spacing)0.4f)
(define-param distort-factor %(distort_factor)0.2f)
(define-param distort-times-hole-spacing (* distort-factor hole-spacing))

(define geo-variable %(geo_variable)i)
(define geo-diamond 1)
(define geo-slab-diamond 2)
(define geo-rods-diamond 3)
(define geo-holes-diamond 4)
(define geo-diamond-dent 5)
(define geo-hole-slab 6)
(define geo-slab-holes-inf-diamond 7)
(define geo-slab-holes-distored 8)
(define k-point-no %(k_index)i)

(define no-of-pos 10)
(define-param pos-start (* -0.5 h-rods)) ; take 5 points within diamond slab
(define-param pos-end 0) 
(define field-loc '()) 
(define z-increment (/ (abs (- pos-end pos-start)) (- no-of-pos 1) ))
(do ((z-index 0 (+ z-index 1))) ((= z-index no-of-pos))
	(set! field-loc (append field-loc (list (vector3 0 0 (+  pos-start (* z-index z-increment) ) ))))
)

;;;;;;;;;;;;;;;;; intensity location grid ;;;;;;;;;;;;;;;;;;

(define no-of-z-pos 100)
(define no-of-x-pos 100)
(define int-no-of-pos (* no-of-z-pos no-of-x-pos)) ; total number of positions sampled

(define-param z-pos-start (/ (* -1 supercell-h) 2) )
(define-param z-pos-end (/ supercell-h 2) )
(define-param x-pos-start (* -0.5 lattice-width))
(define-param x-pos-end (* 0.5 lattice-width)) 
(define int-loc-list '()) 
(do ((z z-pos-start (+ z (/ (abs (- z-pos-end z-pos-start)) no-of-z-pos) ))) ((> z z-pos-end))
	(do ((x x-pos-start (+ x (/ (abs (- x-pos-end x-pos-start)) no-of-x-pos) ))) ((> x x-pos-end))
		(set! int-loc-list (append int-loc-list (list (vector3 x 0 z ))))  ))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


;;;;;;;;;;;;;;;;; epsilon location grid ;;;;;;;;;;;;;;;;;;

(define no-of-x-pos 100)
(define no-of-y-pos 100)
(define int-no-of-pos-horizontal (* no-of-x-pos no-of-y-pos)) ; total number of positions sampled

(define-param y-pos-start (* -0.5 lattice-width) )
(define-param y-pos-end (* 0.5 lattice-width) )
(define-param x-pos-start (* -0.5 lattice-width))
(define-param x-pos-end (* 0.5 lattice-width)) 
(define int-loc-list-horizontal '()) 
(do ((x x-pos-start (+ x (/ (abs (- x-pos-end x-pos-start)) no-of-x-pos) ))) ((> x x-pos-end))
	(do ((y y-pos-start (+ y (/ (abs (- y-pos-end y-pos-start)) no-of-y-pos) ))) ((> y y-pos-end))
		(set! int-loc-list-horizontal (append int-loc-list-horizontal (list (vector3 x y 0 ))))  ))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


(set-param! resolution (vector3 96 96 64))

; triangular lattice with vertical supercell:
(set! geometry-lattice (make lattice (size lattice-width lattice-width supercell-h)
             (basis1 (/ (sqrt 3) 2) 0.5)
             (basis2 (/ (sqrt 3) 2) -0.5)))

(cond 

	(
		(eq? geo-variable geo-diamond)

		(set! geometry
		  (list 
		(make block (material (make dielectric (epsilon diamond)))
		  (center 0 0 0) (size infinity infinity h-diamond))))

	)

	(
		(eq? geo-variable geo-slab-diamond)

		(set! geometry
		   	(list
		(make block (material (make dielectric (epsilon eps)))
		      (center 0 0 (/ h-rods  2)) (size infinity infinity h-rods))
		(make block (material (make dielectric (epsilon diamond)))
		      (center 0 0 (/ (* -1 h-diamond)  2)) (size infinity infinity h-diamond))
		))

	)

	(
		(eq? geo-variable geo-rods-diamond)

		(set! geometry
		  (list (make cylinder (material (make dielectric (epsilon eps)))
		  (center 0 0 (/ h-rods 2)) (radius r) (height h-rods))
		(make block (material (make dielectric (epsilon diamond)))
		  (center 0 0 (/ (* -1 h-diamond)  2)) (size infinity infinity h-diamond))))

	)

	(
		(eq? geo-variable geo-holes-diamond)

		(set! geometry
		      (list
		
		(make block (material (make dielectric (epsilon diamond)))
		      (center 0 0 (/ (* -1 h-diamond)  2)) (size infinity infinity h-diamond))
		(make block (material (make dielectric (epsilon eps)))
		      (center 0 0 0) (size infinity infinity h-rods))
		(make cylinder (material air)
		                  (center 0 0 0) (radius r) (height (* 1  h-rods)))
		))

	)

	(
		(eq? geo-variable geo-diamond-dent)

		(set! geometry
		    (list

				(make block (material (make dielectric (epsilon diamond)))
					(center 0 0 0) (size infinity infinity h-diamond))

				(make cylinder (material air)
					(center 0 0 (/ h-diamond 4)) (radius r) (height (/ h-diamond 2)))


			)
		)

	)

	(
        (eq? geo-variable geo-hole-slab)

        (set! geometry
              (list
        
        (make block (material (make dielectric (epsilon eps)))
              (center 0 0 0) (size infinity infinity h-rods))
        (make cylinder (material air)
                          (center 0 0 0) (radius r) (height (* 1  h-rods)))
        ))

    )

	(
		(eq? geo-variable geo-slab-holes-inf-diamond)

		(set! geometry
		    (list
		
				(make block (material (make dielectric (epsilon diamond)))
				      (center 0 0 (/ (* -1 supercell-h)  4)) (size infinity infinity (/ supercell-h 2)) )
				(make block (material (make dielectric (epsilon eps)))
				      (center 0 0 0) (size infinity infinity h-rods))
				(make cylinder (material air)
				                  (center 0 0 0) (radius r) (height (* 1  h-rods)))
			)
		)

	)

	(
        (eq? geo-variable geo-slab-holes-distored)

        (set! geometry
            (list
        
		        (make block (material (make dielectric (epsilon eps)))
		              (center 0 0 0) (size infinity infinity h-rods))

		        ;hole 1
		        (make cylinder (material air)
		                          (center (* 1 distort-times-hole-spacing) (* -1 distort-times-hole-spacing) 0) (radius r-distort) (height (* 1  h-rods)))
		        ;hole 2
		        (make cylinder (material air)
		                          (center (* 1 distort-times-hole-spacing) (* 0 distort-times-hole-spacing) 0) (radius r-distort) (height (* 1  h-rods)))
		        ;hole 3*
		        (make cylinder (material air)
		                          (center (* 1 hole-spacing) (* 1 hole-spacing) 0) (radius r) (height (* 1  h-rods)))
		        
		        ;hole 4
		        (make cylinder (material air)
		                          (center (* 0 distort-times-hole-spacing) (* -1 distort-times-hole-spacing) 0) (radius r-distort) (height (* 1  h-rods)))
		        ;hole 5**
		        ;(make cylinder (material air)
		        ;                 (center 0 0 0) (radius r) (height (* 1  h-rods)))
		        
		        ;hole 6
		        (make cylinder (material air)
		                          (center (* 0 distort-times-hole-spacing) (* 1 distort-times-hole-spacing) 0) (radius r-distort) (height (* 1  h-rods)))
		        ;hole 7*
		        (make cylinder (material air)
		                          (center (* -1 hole-spacing) (* -1 hole-spacing) 0) (radius r) (height (* 1  h-rods)))
		        
		        ;hole 8
		        (make cylinder (material air)
		                          (center (* -1 distort-times-hole-spacing) (* 0 distort-times-hole-spacing) 0) (radius r-distort) (height (* 1  h-rods)))
		        ;hole 9
		        (make cylinder (material air)
		                          (center (* -1 distort-times-hole-spacing) (* 1 distort-times-hole-spacing) 0) (radius r-distort) (height (* 1  h-rods)))


        	)
        )

    )


)





; 1st Brillouin zone of a triangular lattice:
(define Gamma (vector3 0 0 0))
(define M (vector3 0 0.5 0))
(define K (vector3 (/ -3) (/ 3) 0))

(define-param k-interp %(k_interp)i)   ; the number of k points to interpolate if full cut taken

(define k-list (interpolate k-interp (list Gamma M K Gamma)))

(if (eq? single-point 1)
; if only single point taken at K
(set! k-points (list (list-ref k-list k-point-no)))
; if want linear cut in BZ:
(set! k-points (interpolate k-interp (list Gamma M K Gamma)))
)

;(define k-points '())
;(define x-grid 30)
;(define y-grid 30)
;(do ((x 0 (+ x 1))) ((= x (+ x-grid 1)))
; (do ((y 0 (+ y 1))) ((= y (+ y-grid 1)))
;      (set! k-points (append k-points (list (vector3 (+ 0 (* (/ (/ -3) y-grid) y)) (- (* (/ (/ 2) x-grid) x) (* (/ (/ 6) y-grid) y) ) 0 ))))  ))

(set! num-bands no-of-bands)


(print "eigdata:,kx,ky,")

(do ((band-no 1 (+ band-no 1))) ((= band-no (+ no-of-bands 1)))
(print "fband" band-no ",")

	(do ((pos-no 1 (+ pos-no 1))) ((= pos-no (+ no-of-pos 1)))
	(print "band" band-no "-R" pos-no "-x,band" band-no "-R" pos-no "-y,band" band-no "-R" pos-no "-z,"   ) 
	)

	(do ((int-pos-no 1 (+ int-pos-no 1))) ((= int-pos-no (+ int-no-of-pos 1)))
	(print "band" band-no "-I" int-pos-no ",") 
	)

)


(print "\\n")


(define (output-epsilon-at-r)

	(print "\\n")

	(print "atomloc:")
	(print ",supercell-h")
	(do ((z-index 0 (+ z-index 1))) ((= z-index no-of-pos))
		(print ",loc" (+ z-index 1))
	)
	(print "\\n")

	(print "atomloc:")
	(print "," supercell-h)
	(do ((z-index 0 (+ z-index 1))) ((= z-index no-of-pos))
		(print "," (vector-ref (list-ref field-loc z-index) 2) )
	)
	(print "\\n")

	(print "epsout:")
	(do ((int-pos-no 1 (+ int-pos-no 1))) ((= int-pos-no int-no-of-pos))
		(print ",epsValue") 
	)
	(print "\\n")

	(print "epsout:")
	(do ((int-pos-no 0 (+ int-pos-no 1))) ((= int-pos-no int-no-of-pos))
	    (let ((epsilon-local-value (get-epsilon-point (list-ref int-loc-list int-pos-no) )))
		    (print ","  epsilon-local-value) 
	    )
    )
    (print "\\n")

	(print "epsout:")
	(do ((int-pos-no 0 (+ int-pos-no 1))) ((= int-pos-no int-no-of-pos-horizontal))
	    (let ((epsilon-local-value (get-epsilon-point (list-ref int-loc-list-horizontal int-pos-no) )))
		    (print ","  epsilon-local-value) 
	    )
    )
    (print "\\n")
  
)


(define (square x) ;define square function
  (* x x))


(define (output-at-r x)
(print "eigdata:, " (exact->inexact (vector-ref current-k 0)) "," (exact->inexact (vector-ref current-k 1)))

(do ((band-no 1 (+ band-no 1))) ((= band-no (+ no-of-bands 1)))
(print "," (list-ref freqs (- band-no 1))   )
    (get-efield band-no)

    (do ((pos-no 0 (+ pos-no 1))) ((= pos-no no-of-pos))
	    (let ((myfield (get-bloch-field-point (list-ref field-loc pos-no) )))
	    (print "," (vector-ref myfield 0) "," (vector-ref myfield 1) "," (vector-ref myfield 2))
	    )
    )

	(do ((int-pos-no 0 (+ int-pos-no 1))) ((= int-pos-no int-no-of-pos))
	    (let ((myintensity (get-bloch-field-point (list-ref int-loc-list int-pos-no) )))
	    (print "," (+ (square (magnitude (vector-ref myintensity 0))) (+ (square (magnitude (vector-ref myintensity 1))) (square (magnitude (vector-ref myintensity 2))) ) )   ) 
	    )
    )
)

(print "\\n" )
)

; Run even and odd bands.
(set! output-epsilon (lambda () (output-epsilon-at-r)))
(begin-time ;
	(run-zeven fix-efield-phase output-at-r)
)
(display-eigensolver-stats) """%params
###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################

		mpb_script_name = "mpb_%s"%current_name
		# write the script file
		f2 = open(this_dir + "//%s.ctl"%mpb_script_name,"w")
		f2.write(mpb_script)
		f2.close()



		cmd_str = "sbatch %s.sh %s.ctl data.out" %(slurm_name,mpb_script_name)
		proc = subprocess.Popen(cmd_str,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)                    
		proc.wait()

		#local use on my MAC:
		# f3 = open(this_dir + "//data.out","w")
		# f3.write("eigdata here 1234")
		# f3.close()

		os.chdir(dirroot)

	if mode=="fetch":


		os.chdir(this_dir)

		command2 = "grep eigdata data.out > %s.dat"%current_name
		proc = subprocess.Popen(command2,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)                   
		proc.wait()

		if k_index == 0:
			command2 = "grep epsout data.out > epsout.dat"
			proc = subprocess.Popen(command2,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)                   
			proc.wait()

			command2 = "grep atomloc data.out > atomloc.dat"
			proc = subprocess.Popen(command2,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)                   
			proc.wait()


		command3 = "cp ./*.dat ../"
		proc = subprocess.Popen(command3,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)                   
		proc.wait()

		command4 = "rm *"
		proc = subprocess.Popen(command4,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)                   
		proc.wait()

		os.chdir(dirroot)


		command4 = "rmdir %s"%this_dir

		# print command4
		proc = subprocess.Popen(command4,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)                   
		proc.wait()

	if mode=="fuse":

		fuse_date_name = 'data_all' #name of fused data

		if k_index == 0:
			command6 = "touch %s.dat"%fuse_date_name #create target file
			proc = subprocess.Popen(command6,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)                   
			proc.wait()
		else:
			command5 = "sed -i '/kx/d' ./%s.dat"%current_name #remove header line (NB: might need to remove first '' on cluster 
			proc = subprocess.Popen(command5,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)                   
			proc.wait()

		command7 = "grep eigdata %s.dat >> %s.dat"%(current_name,fuse_date_name) #append data
		proc = subprocess.Popen(command7,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)                   
		proc.wait()

		command8 = "rm %s.dat"%current_name #remove file 
		proc = subprocess.Popen(command8,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)                   
		proc.wait()




