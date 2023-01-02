use kursach;

CREATE TABLE provider_name (
	provider_id INT AUTO_INCREMENT,
	name VARCHAR(50),
	
	PRIMARY KEY (provider_id)
);

CREATE TABLE provider_address (
	provider_id INT,
	address TEXT,
	
	FOREIGN KEY (provider_id) REFERENCES provider_name(provider_id) ON DELETE CASCADE
);

CREATE TABLE flower (
	flower_id INT AUTO_INCREMENT,
	name VARCHAR(50),
	price INT,
	provider_id INT,
	
	PRIMARY KEY (flower_id),
	UNIQUE (name),
	FOREIGN KEY (provider_id) REFERENCES provider_name(provider_id) ON DELETE CASCADE
);

CREATE TABLE customer_name (
	customer_id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(50)
);

CREATE TABLE customer_info (
	customer_id INT,
	phone VARCHAR(20),
	address TEXT,
	
	FOREIGN KEY (customer_id) REFERENCES customer_name(customer_id) ON DELETE CASCADE
);


CREATE TABLE contract (
	contract_id INT AUTO_INCREMENT,
	customer_id INT,
	register_date DATE,
	execution_date DATE,
	
	PRIMARY KEY (contract_id),
	FOREIGN KEY (customer_id) REFERENCES customer_name(customer_id) ON DELETE CASCADE
);

CREATE TABLE booking (
    booking_id INT AUTO_INCREMENT,
	contract_id INT,
	flower_id INT,
	quantity INT,
	
	PRIMARY KEY (booking_id),
	FOREIGN KEY (contract_id) REFERENCES contract(contract_id) ON DELETE CASCADE,
	FOREIGN KEY (flower_id) REFERENCES flower(flower_id) ON DELETE CASCADE
);


CREATE TABLE employee (
	login VARCHAR(50),
	password VARCHAR(50),
	job_title VARCHAR(100),
	
	PRIMARY KEY (login)
);

CREATE TABLE customer_user (
	login VARCHAR(50),
	password VARCHAR(50),
	customer_id INT,
	
	PRIMARY KEY (login),
	FOREIGN KEY (customer_id) REFERENCES customer_name(customer_id)
);

INSERT INTO employee VALUES(
	"admin", "admin123", "manager"
);

INSERT INTO employee VALUES(
	"worker1", "321", "worker"
);

INSERT INTO provider_name(name) VALUES(
	"provider1"
);

INSERT INTO provider_address VALUES(
	1, "Street1"
);

INSERT INTO provider_address VALUES(
	1, "Street2"
);