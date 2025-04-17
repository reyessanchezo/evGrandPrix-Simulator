(load "./vesc.lisp")

;; Source: https://stackoverflow.com/a/73687213
(defun round-n (v &optional (n 0)) ;; Set n as an optional parameter
  ;; These declarations are really to show intent: FLOAT is not enough
  ;; to optimize although perhaps a good type-inferencing compiler can
  ;; work out that this takes double->double &c.
  "Example: 
  v = 2.345
  n = 2
  xp = 1/100
  (fround 2.345 xp) = 235 -0.004
  return: 235 * 1 / 100"
  (declare (type float v)
           (type (integer 0) n)) ;; Checking data types
  (let ((xp (expt 10 (- n)))) ;; 10^-n
    (* (fround v xp)
       xp)))

(defun test-rpm-to-v-0 ()
  (print (rpm-to-v 0)))

(defun test-rpm-to-v-10 ()
  (print (rpm-to-v 10)))

(defun test-rpm-to-v-100 ()
  (print (rpm-to-v 100)))

(defun test-rpm-to-v-500 ()
  (print (rpm-to-v 500)))

(defun test-rpm-to-v-1000 ()
  (print (rpm-to-v 1000)))

(defun test-rpm-to-v-2000 ()
  (print (rpm-to-v 2000)))

(defun test-rpm-0 ()
  (print (braking-force 0 0)))

(defun test-rpm-250 ()
  (print (braking-force 250 0)))

(defun test-rpm-500 ()
  (print (braking-force 500 0)))

(defun test-rpm-750 ()
  (print (braking-force 750 0)))

(defun test-rpm-1000 ()
  (print (braking-force 1000 0)))

(defun test-rpm-1500 ()
  (print (braking-force 1500 0)))

(defun test-rpm-2000 ()
  (print (braking-force 2000 0)))

(defun test-rpm-5000 ()
  (print (braking-force 5000 0)))

(test-rpm-to-v-0)
(test-rpm-to-v-100)
(test-rpm-to-v-1000)
(test-rpm-to-v-2000)

(test-rpm-0)
(test-rpm-500)
(test-rpm-1000)
