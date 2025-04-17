;; Node Structure { data, next, prev }
(defstruct node
  data
  (next nil)
  (prev nil))

;; Queue structure pointer to the front and rear nodes and the counter.
(defstruct (queue (:constructor %make-queue))
  (front nil)
  (rear nil)
  (size 0)
  (sum 0))

(defun make-queue ()
  "Create and return a new empty queue."
  (%make-queue))

(defun queue-empty-p (queue)
  "Return T if QUEUE is empty, NIL otherwise."
  (= (queue-size queue) 0))

(defun enqueue (queue item)
  "Add ITEM to the rear of QUEUE. Return QUEUE."
  (declare (type number item))
  (let ((new-node (make-node :data item))) ;; Creates new node
    (if (queue-empty-p queue)
        ;; If queue is empty, new node becomes both front and rear
        (setf (queue-front queue) new-node
              (queue-rear queue) new-node) ;; Sets both the rear and the front to the new-node.
        ;; Otherwise, add to rear
        (let ((old-rear (queue-rear queue))) ;; Get the old rear node
          (setf (node-next old-rear) new-node ;; Set the old rear node next to the new node 
                (node-prev new-node) old-rear ;; Set the new node prev to the old node
                (queue-rear queue) new-node))) ;; Set the rear to the new node
    ;; Increment size
    (incf (queue-size queue))
    (incf (queue-sum queue) item)
    ;; Return queue
    queue))

(defun dequeue (queue)
  "Remove and return the front item of QUEUE. 
Signal an error if QUEUE is empty."
  (if (queue-empty-p queue)
      (error "Cannot dequeue from empty queue.")
      (let* ((front-node (queue-front queue))
             (result (node-data front-node)))
        ;; Decrease the sum
        (decf (queue-sum queue) (node-data (queue-front queue)))
        ;; Update front pointer
        (setf (queue-front queue) (node-next front-node))
        ;; If queue is now empty, update rear pointer as well
        (if (null (queue-front queue))
            (setf (queue-rear queue) nil)
            ;; Otherwise, clear prev pointer of new front
            (setf (node-prev (queue-front queue)) nil))
        ;; Decrement size
        (decf (queue-size queue))
        result)))

(defun get-average (queue)
  "Return the average of all the elements in the QUEUE."
  (if (queue-empty-p queue)
      (error "Cannot find the average with size 0.")
      (/ (float (queue-sum queue)) (queue-size queue))))

(defun queue-to-list (queue)
  "Return a new list containing all items in QUEUE, from front to rear."
  (let ((result nil)
        (current (queue-front queue)))
    (loop while current do
      (push (node-data current) result)
      (setf current (node-next current)))
    (nreverse result)))

;; Actual code
(defpackage :dyno
  (:use :cl)
  (:export :breaking-force
           :get-dvdt))

;; Kart Specifications
(defconstant *D_t* 0.3) ; Kart tire diameter in meters
(defvar *Gr* (/ 13 55)) ; Gearing ratio
(defvar *P* 1) ; Tire pressure (barr)
(defvar *rho* 1.2) ; Air density (kg/m^3)
(defvar *m* 200) ; Kart mass (kg)
(defvar *g* 9.8) ; Gravity acceleration constant (m/s^2)
(defvar *C_d* 0.8) ; Drag coefficient (unitless)
(defvar *A* 0.5) ; Maximum cross-sectional area (m^2)

;; Testing locally
(defun get-rpm ()
  1000)

(defun get-vin ()
  45)

(defun set-brake (current)
  0)

(defparameter *response-rate* 0.001)
(defconstant +pi+ 3.14159)

(defun rpm-to-rps (rpm)
  "Convert RPM to RPS."
  (/ rpm 60))

(defun rpm-to-v (rpm)
  "Converts rpm to velocity in m/s. v = G w_m PI D_t"
  (let ((rps (rpm-to-rps rpm)))
    (format t "M/S: ~A~%" (* *Gr* rps +pi+ *D_T*))
    (* *Gr* rps +pi+ *D_t*)))

(defun braking-force (rpm dvdt)
  "Calculates breaking force during accelration. 
  (0.005 + (1/P) (0.01 + 0.0095 ((3.6) v / 100)^2)) m g + (1/2) C_d A v^2 + m (dv/dt) = (2 T n/Dt)(w_motor / w_wheel)
  term-1: "
  (let* ((v (rpm-to-v rpm))
         (term1-1 (+ 0.01 (* 0.0095 (expt (/ (* 3.6 v) 100) 2))))
         (term1-2 (+ 0.005 (* (/ 1 *P*) term1-1)))
         (term1 (* term1-2 *m* *g*))
         (term2 (/ (* *C_d* *A* *rho* (* v v)) 2))
         (term3 (* *m* dvdt))
         (result (+ term1 term2 term3)))
         ;; (format t "v: ~A | m: ~A | g: ~A ~%" v *m* *g*)
         ;; (format t "term 1-1: ~A~%" term1-1)
         ;; (format t "term 1-2: ~A~%" term1-2)
         ;; (format t "term 1: ~A~%" term1)
         ;; (format t "term 2: ~A~%" term2)
    result))

(defparameter *prev-v* 0)

(defun get-dvdt (curr-v)
  "Get rise over run"
  (let* ((term-1 (- curr-v *prev-v*))
        (result (/ term-1 *response-rate*)))
        ;; (format t "term-1 ~A~%" term-1)
        ;; (format t "DV/DT: ~A~%" result)
        (setf *prev-v* curr-v)
    result))

;; (get-vin): Get input voltage:  
;; (get-rpm) Get motor eRPM. Negative values mean that the motor spins in the reverse direction.
;; (set-brake current) Set braking current
(defvar *q* (make-queue))
(defun main ()
  (loop for i from 1 to 10
    do (enqueue *q* 0)) 

  (format t "~%" rpm)
  (loop for i from 1 to 100
    do 
      (let* ((rpm (/ (get-rpm) 1))
            (bc (braking-force rpm (get-dvdt rpm)))
            (bc-amps (/ bc (get-vin)))) ;; Amps = wattage / voltage
        (format t "RPM: ~A | " rpm)
        (format t "Brake force (W): ~A | " bc)
        (format t "Brake force (A): ~A | " bc-amps)
        (dequeue *q*)
        (enqueue *q* bc-amps))
       (let ((avg (get-average *q*)))
        (set-brake avg)
        (format t "Size: ~A | " (queue-size *q*))
        (format t "Avg (A): ~A~%" avg))
       (sleep *response-rate*)
       ))

(main)
