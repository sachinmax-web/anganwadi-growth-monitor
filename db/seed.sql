-- =============================================================
-- Seed Data — realistic Tamil Nadu anganwadi records
-- =============================================================
PRAGMA foreign_keys = ON;

-- Centres
INSERT INTO anganwadi_centre (name, village, district, state) VALUES
  ('Centre A - Kovilpatti',  'Kovilpatti',  'Thoothukudi', 'Tamil Nadu'),
  ('Centre B - Srivaikundam','Srivaikundam','Thoothukudi', 'Tamil Nadu');

-- Workers
INSERT INTO worker (centre_id, full_name, phone, active, joined_on) VALUES
  (1, 'Meenakshi Rajan',  '9876543210', 1, '2019-06-01'),
  (1, 'Sumathi Devi',     '9876543211', 1, '2021-03-15'),
  (2, 'Kalaivani Muthu',  '9876543212', 1, '2020-01-10');

-- Children (ages 6 months – 5 years, mix of M/F)
INSERT INTO child (centre_id, full_name, date_of_birth, sex, guardian, enrolled_on) VALUES
  (1, 'Arjun Kumar',    '2022-01-10', 'M', 'Ravi Kumar',    '2022-03-01'),
  (1, 'Priya Selvam',   '2021-07-22', 'F', 'Selvam T',      '2021-09-01'),
  (1, 'Karthik Babu',   '2023-03-05', 'M', 'Babu R',        '2023-05-01'),
  (1, 'Deepika Raj',    '2022-09-18', 'F', 'Raj S',         '2022-11-01'),
  (1, 'Surya Anand',    '2021-12-01', 'M', 'Anand P',       '2022-02-01'),
  (2, 'Lakshmi Nair',   '2022-04-14', 'F', 'Nair K',        '2022-06-01'),
  (2, 'Vishal Mohan',   '2023-01-20', 'M', 'Mohan D',       '2023-03-01'),
  (2, 'Anitha Perumal', '2021-08-30', 'F', 'Perumal V',     '2021-10-01'),
  (2, 'Dinesh Siva',    '2022-06-11', 'M', 'Siva G',        '2022-08-01'),
  (2, 'Kavya Krishnan', '2023-05-25', 'F', 'Krishnan M',    '2023-07-01');

-- Growth Measurements — 6 months of history per child
-- Child 1: Arjun Kumar — steady normal growth
INSERT INTO growth_measurement (child_id,worker_id,measured_on,weight_kg,height_cm,muac_cm) VALUES
  (1,1,'2024-01-15',8.2,72.0,13.5),(1,1,'2024-02-15',8.5,72.8,13.7),
  (1,1,'2024-03-15',8.7,73.5,13.8),(1,1,'2024-04-15',9.0,74.2,14.0),
  (1,1,'2024-05-15',9.2,74.9,14.1),(1,1,'2024-06-15',9.5,75.5,14.3);

-- Child 2: Priya Selvam — mild wasting trend
INSERT INTO growth_measurement (child_id,worker_id,measured_on,weight_kg,height_cm,muac_cm) VALUES
  (2,1,'2024-01-15',9.8,80.0,13.2),(2,1,'2024-02-15',9.7,80.4,13.0),
  (2,1,'2024-03-15',9.6,80.8,12.8),(2,1,'2024-04-15',9.5,81.0,12.5),
  (2,1,'2024-05-15',9.4,81.2,12.3),(2,1,'2024-06-15',9.3,81.5,12.1);

-- Child 3: Karthik Babu — SAM risk, consistently low
INSERT INTO growth_measurement (child_id,worker_id,measured_on,weight_kg,height_cm,muac_cm) VALUES
  (3,2,'2024-01-15',5.1,58.0,11.2),(3,2,'2024-02-15',5.0,58.5,11.0),
  (3,2,'2024-03-15',5.0,59.0,10.9),(3,2,'2024-04-15',4.9,59.3,10.8),
  (3,2,'2024-05-15',4.9,59.5,10.7),(3,2,'2024-06-15',4.8,59.7,10.5);

-- Child 4: Deepika Raj — normal, good gain
INSERT INTO growth_measurement (child_id,worker_id,measured_on,weight_kg,height_cm,muac_cm) VALUES
  (4,2,'2024-01-15',7.5,70.0,13.8),(4,2,'2024-02-15',7.8,70.8,14.0),
  (4,2,'2024-03-15',8.1,71.5,14.2),(4,2,'2024-04-15',8.4,72.3,14.3),
  (4,2,'2024-05-15',8.7,73.0,14.5),(4,2,'2024-06-15',9.0,73.8,14.7);

-- Child 5: Surya Anand — stagnant weight (MAM)
INSERT INTO growth_measurement (child_id,worker_id,measured_on,weight_kg,height_cm,muac_cm) VALUES
  (5,1,'2024-01-15',8.9,78.0,12.6),(5,1,'2024-02-15',9.0,78.5,12.6),
  (5,1,'2024-03-15',9.0,79.0,12.5),(5,1,'2024-04-15',9.1,79.5,12.5),
  (5,1,'2024-05-15',9.1,80.0,12.4),(5,1,'2024-06-15',9.1,80.3,12.4);

-- Child 6: Lakshmi Nair — normal
INSERT INTO growth_measurement (child_id,worker_id,measured_on,weight_kg,height_cm,muac_cm) VALUES
  (6,3,'2024-01-15',7.8,71.0,13.9),(6,3,'2024-02-15',8.1,71.8,14.1),
  (6,3,'2024-03-15',8.4,72.5,14.3),(6,3,'2024-04-15',8.7,73.2,14.4),
  (6,3,'2024-05-15',9.0,74.0,14.6),(6,3,'2024-06-15',9.3,74.7,14.8);

-- Child 7: Vishal Mohan — recovering, was low
INSERT INTO growth_measurement (child_id,worker_id,measured_on,weight_kg,height_cm,muac_cm) VALUES
  (7,3,'2024-01-15',4.8,56.0,10.8),(7,3,'2024-02-15',5.0,56.8,11.0),
  (7,3,'2024-03-15',5.3,57.5,11.4),(7,3,'2024-04-15',5.6,58.2,11.8),
  (7,3,'2024-05-15',5.9,59.0,12.1),(7,3,'2024-06-15',6.2,59.8,12.5);

-- Child 8: Anitha Perumal — weight loss alert
INSERT INTO growth_measurement (child_id,worker_id,measured_on,weight_kg,height_cm,muac_cm) VALUES
  (8,3,'2024-01-15',10.2,82.0,13.5),(8,3,'2024-02-15',10.0,82.4,13.2),
  (8,3,'2024-03-15',9.8,82.8,13.0),(8,3,'2024-04-15',9.5,83.0,12.8),
  (8,3,'2024-05-15',9.3,83.3,12.6),(8,3,'2024-06-15',9.0,83.5,12.3);

-- Child 9: Dinesh Siva — borderline MAM
INSERT INTO growth_measurement (child_id,worker_id,measured_on,weight_kg,height_cm,muac_cm) VALUES
  (9,3,'2024-01-15',7.2,68.0,12.5),(9,3,'2024-02-15',7.3,68.5,12.5),
  (9,3,'2024-03-15',7.3,69.0,12.4),(9,3,'2024-04-15',7.4,69.5,12.4),
  (9,3,'2024-05-15',7.4,70.0,12.3),(9,3,'2024-06-15',7.5,70.3,12.3);

-- Child 10: Kavya Krishnan — normal infant
INSERT INTO growth_measurement (child_id,worker_id,measured_on,weight_kg,height_cm,muac_cm) VALUES
  (10,3,'2024-01-15',5.5,60.0,12.8),(10,3,'2024-02-15',5.8,61.0,13.0),
  (10,3,'2024-03-15',6.1,62.0,13.2),(10,3,'2024-04-15',6.4,63.0,13.4),
  (10,3,'2024-05-15',6.7,64.0,13.6),(10,3,'2024-06-15',7.0,65.0,13.8);

-- Nutrition Status rows (derived from measurements above)
-- measurement_ids 1-6 = child 1, 7-12 = child 2, etc.
INSERT INTO nutrition_status (measurement_id,status,waz_score,determined_by) VALUES
  (1,'Normal',-0.5,'system'),(2,'Normal',-0.4,'system'),(3,'Normal',-0.4,'system'),
  (4,'Normal',-0.3,'system'),(5,'Normal',-0.3,'system'),(6,'Normal',-0.2,'system'),
  (7,'MAM',-2.1,'system'),(8,'MAM',-2.2,'system'),(9,'MAM',-2.3,'system'),
  (10,'MAM',-2.4,'system'),(11,'MAM',-2.5,'system'),(12,'MAM',-2.6,'system'),
  (13,'SAM',-3.2,'system'),(14,'SAM',-3.3,'system'),(15,'SAM',-3.4,'system'),
  (16,'SAM',-3.5,'system'),(17,'SAM',-3.5,'system'),(18,'SAM',-3.6,'system'),
  (19,'Normal',-0.8,'system'),(20,'Normal',-0.7,'system'),(21,'Normal',-0.6,'system'),
  (22,'Normal',-0.5,'system'),(23,'Normal',-0.4,'system'),(24,'Normal',-0.3,'system'),
  (25,'MAM',-2.0,'system'),(26,'MAM',-2.0,'system'),(27,'MAM',-2.1,'system'),
  (28,'MAM',-2.1,'system'),(29,'MAM',-2.2,'system'),(30,'MAM',-2.2,'system'),
  (31,'Normal',-0.9,'system'),(32,'Normal',-0.8,'system'),(33,'Normal',-0.7,'system'),
  (34,'Normal',-0.6,'system'),(35,'Normal',-0.5,'system'),(36,'Normal',-0.4,'system'),
  (37,'SAM',-3.5,'system'),(38,'SAM',-3.3,'system'),(39,'MAM',-2.9,'system'),
  (40,'MAM',-2.6,'system'),(41,'MAM',-2.3,'system'),(42,'Normal',-2.0,'system'),
  (43,'MAM',-2.4,'system'),(44,'MAM',-2.5,'system'),(45,'MAM',-2.6,'system'),
  (46,'SAM',-3.0,'system'),(47,'SAM',-3.1,'system'),(48,'SAM',-3.3,'system'),
  (49,'MAM',-2.0,'system'),(50,'MAM',-2.0,'system'),(51,'MAM',-2.1,'system'),
  (52,'MAM',-2.1,'system'),(53,'MAM',-2.2,'system'),(54,'MAM',-2.2,'system'),
  (55,'Normal',-1.2,'system'),(56,'Normal',-1.1,'system'),(57,'Normal',-1.0,'system'),
  (58,'Normal',-0.9,'system'),(59,'Normal',-0.8,'system'),(60,'Normal',-0.7,'system');

-- Referrals for high-risk children
INSERT INTO referral (child_id,raised_by,raised_on,reason,resolved_on,outcome) VALUES
  (3,2,'2024-03-20','SAM — weight below -3 SD for 3 consecutive months','2024-05-10','NRC admission, supplementary feeding started'),
  (2,1,'2024-04-18','MAM — consistent weight loss over 4 visits',NULL,NULL),
  (8,3,'2024-05-15','Weight loss for 5 consecutive months, MUAC < 12.5',NULL,NULL);
