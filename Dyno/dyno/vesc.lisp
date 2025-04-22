;; 01 -- Constants
(define *D_t* 0.254) ; Kart tire diameter in meters
(define *Gr* (/ 9.0 68)) ; Gearing ratio
(define *P* 1.0) ; Tire pressure (barr)
(define *rho* 1.2) ; Air density (kg/m^3)
(define *m* 161.78) ; Kart mass (kg)
(define *g* 9.8) ; Gravity acceleration constant (m/s^2)
(define *C_d* 0.8) ; Drag coefficient (unitless)
(define *A* 0.7) ; Maximum cross-sectional area (m^2)
(define *mu_s* 0.5416306095) ; Static Friction coefficient

;; 02 -- User defined variables
(define can-flag 0) ;; 0: Turn, 1: Straight
(define +pi+ 3.14159)
(define prev-v 0.0)
(define print-output "")
(define queue-size 10)
(define response-rate 0.01)

;; 03 -- List (Queue) functions
(define make-list
    (lambda (n val)
    (if (= n 0)
        nil
        (cons val (make-list (- n 1) val))
    )
    ))
    
;; Append element to the end of the list
;; Description: Ignore the first element and return a list with the rest of the elements plus the new one.
(define nq
    (lambda (lst ele)
        (append (rest lst) (list ele))))

;; Return the sum of all the elements in the list
(define lsum
    (lambda (lst)
    (eval (cons '+ lst))))

;; Get the average of all the elements in the list
(define get-avg
    (lambda (lst)
        (/ (lsum lst) (to-float (length lst)))
    ))

;; 04 -- CAN event handling
;; When a packet is received, set the `can-flag` variable to the value of the first byte in the packet.
(define proc-sid (lambda (id data)
    (setvar 'can-flag (bufget-i8 data 0))
))

;; 
(define event-handler (lambda ()
    (progn
        (recv ((event-can-sid (? id) . (? data)) (proc-sid id data))
        (_ nil))
    (event-handler)
)))

;; 05 -- Deceleration
(define a (* -0.99 *g* *mu_s*))
(define dec (* a (/ 6 (* *D_t* *Gr*)))) ; rps per second * res

;; Decrease the RPM linearly
(define deceleration
    (lambda (rpm)
        (+ rpm dec)
    )
)

;; 06 -- Braking force
;; RPM to RPS
(defun rpm-to-rps (rpm)
  (/ rpm 60))

;; RPM to M/S^2
(defun rpm-to-v (rpm)
  (let ((rps (rpm-to-rps rpm)))
    (* *Gr* rps +pi+ *D_t*)))

;; Physical forces applied to the kart
;; Aerodynamic Drag, Rolling resistance, Inertia
(define braking-force
  (lambda (rpm dvdt)
    (let ((v (rpm-to-v rpm))
          (term1-1 (/ (* 3.6 v) 100.0))
          (term1-2 (+ 0.01 (* 0.0095 (* term1-1 term1-1))))
          (term1-3 (+ 0.005 (* (/ 1 *P*) term1-2)))
          (term1 (* term1-3 *m* *g*))
          (term2 (/ (* *C_d* *A* *rho* (* v v)) 2))
          (term3 (* *m* dvdt))
          (term4 (+ term1 term2 term3))
          (result (* term4 v)))  ;; Correctly defining `result`
      result)))  ;; Returning `result`

;; 07 -- Rate of change of velocity
(define get-dvdt
  (lambda (curr-rpm)
    (let ((curr-v (rpm-to-v curr-rpm))
          (term-1 (- curr-v prev-v))
          (result (/ term-1 response-rate)))
      (setvar 'prev-v curr-v)
      result)))

;; 08 -- Print stats
(defun print-stats ()
   (progn
        (if (not-eq print-output "")
          (print print-output)
        )
        (sleep 0.5)
        (print-stats)
   )
)

;; 09 -- Main loop
(print "Start!!!")
(define q (make-list queue-size 0)) ;; Create a queue of size `queue-size`

(defun main ()
    (loopwhile t
        (progn
            (if (eq can-flag 0)
                (let ((rpm (/ (get-rpm) 5.0))
                      (output (str-merge "(TURN) RPM: " (str-from-n rpm)))
                       (new-rpm (deceleration rpm))) ; TODO
                    (progn
                        (if (> new-rpm 0)
                            (set-rpm new-rpm)
                        )
                        (setvar 'print-output output)
                    )
                )
                (let ((rpm (/ (get-rpm) 5.0))
                    (dv-dt (get-dvdt rpm))
                    (bf (braking-force rpm dv-dt))
                    (bf-amps (/ bf (get-vin)))
                    (output (str-merge "RPM: " (str-from-n rpm) " | BF (W): " (str-from-n bf) " | BF (A): " (str-from-n bf-amps))))
                    (progn
                        (setvar 'q (nq q bf-amps))
                        (set-brake (get-avg q))
                        (setvar 'print-output output)
                    )
                )
            )
            (sleep response-rate)
        )
    )
)

;; Start listening to CAN events
(event-register-handler (spawn event-handler))
(event-enable 'event-can-sid)
;; Start printing stats
(spawn print-stats)
;; Run main loop
(main)

;; Additional comments
;; 1. There is no difference between defun and define variables with lambda functions.
;; 2. A queue with bigger queue size will give a smoother output, however, the "response time" will be slower. (Try to keep it as low as possible)
;; 3. The VESC uses eid in CAN by default. However, the code is written to use sid.
