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

(defvar *q* (make-queue))
(enqueue *q* 0)
(enqueue *q* 1)
(enqueue *q* 2)
(enqueue *q* 3)
(format t "Sum: ~a~%" (queue-sum *q*))
(format t "Average: ~a~%" (get-average *q*))
(format t "Dequeued: ~a~%" (dequeue *q*))
(format t "Dequeued: ~a~%" (dequeue *q*))
(format t "Dequeued: ~a~%" (dequeue *q*))
(format t "Dequeued: ~a~%" (dequeue *q*))
(format t "Sum: ~a~%" (queue-sum *q*))

;; (enqueue *q* 'b)
;; (enqueue-front *q* 'z)
;; (queue-to-list *q*)  ;; => (Z A B)
;; (dequeue *q*)        ;; => Z
;; (dequeue-rear *q*)   ;; => B
;; (queue-front *q*)    ;; => A
