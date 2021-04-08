-- Tablas relacionadas a la metadata de un bucket de
-- tema y deficiencia (etiqueta) para examen de admision
CREATE TABLE bucket_tema_adm(
    id BIGINT(20) UNSIGNED PRIMARY KEY NOT NULL AUTO_INCREMENT,
    id_examen_admision BIGINT(20) UNSIGNED NOT NULL,
    FOREIGN KEY(id_examen_admision) REFERENCES examen_admision(id)
);

CREATE TABLE bucket_tema_adm_detalle(
    id BIGINT(20) UNSIGNED PRIMARY KEY NOT NULL AUTO_INCREMENT,
    bucket_tema_adm_id BIGINT(20) UNSIGNED NOT NULL,
    tema_id BIGINT(20) UNSIGNED NOT NULL,
    FOREIGN KEY(bucket_tema_adm_id) REFERENCES bucket_tema_adm(id),
    FOREIGN KEY(tema_id) REFERENCES temas(id)
);

CREATE TABLE bucket_deficiencia_adm(
    id BIGINT(20) UNSIGNED PRIMARY KEY NOT NULL AUTO_INCREMENT,
    bucket_tema_adm_id BIGINT(20) UNSIGNED NOT NULL,
    etiqueta_id BIGINT(20) UNSIGNED NOT NULL,
    FOREIGN KEY(bucket_tema_adm_id) REFERENCES bucket_tema_adm(id),
    FOREIGN KEY(etiqueta_id) REFERENCES etiquetas(id) 
);

CREATE TABLE bucket_tema_pregunta_adm(
    id BIGINT(20) UNSIGNED PRIMARY KEY NOT NULL AUTO_INCREMENT,
    bucket_tema_adm_id BIGINT(20) UNSIGNED NOT NULL,
    pregunta_examen_adm_id BIGINT(20) UNSIGNED NOT NULL,
    FOREIGN KEY(bucket_tema_adm_id) REFERENCES bucket_tema_adm(id),
    FOREIGN KEY(pregunta_examen_adm_id) REFERENCES pregunta_examen_admision(id)
);

CREATE TABLE bucket_deficiencia_literal_adm(
    id BIGINT(20) UNSIGNED PRIMARY KEY NOT NULL AUTO_INCREMENT,
    bucket_deficiencia_adm_id BIGINT(20) UNSIGNED NOT NULL,
    respuesta_examen_adm_id BIGINT(20) UNSIGNED NOT NULL,
    FOREIGN KEY(bucket_deficiencia_adm_id) REFERENCES bucket_deficiencia_adm(id),
    FOREIGN KEY(respuesta_examen_adm_id) REFERENCES respuesta_examen_admision(id)
);

-- Tablas relacionadas con el almacenado de informacion
-- para las distintas capas a soportar

-- Capas para instituciones
CREATE TABLE bucket_tema_adm_instituto(
    id BIGINT(20) UNSIGNED PRIMARY KEY NOT NULL AUTO_INCREMENT,
    bucket_tema_adm_id BIGINT(20) UNSIGNED NOT NULL,
    institucion_id BIGINT(20) UNSIGNED NOT NULL,
    preguntas INT,
    preguntas_masculino INT,
    preguntas_femenino INT,
    aciertos INT,
    aciertos_masculino INT,
    aciertos_femenino INT,
    fallos INT,
    fallos_masculino INT,
    fallos_femenino INT,
    FOREIGN KEY(bucket_tema_adm_id) REFERENCES bucket_tema_adm(id),
    FOREIGN KEY(institucion_id) REFERENCES instituciones(id)
);

CREATE TABLE bucket_deficiencia_adm_instituto(
    id BIGINT(20) UNSIGNED PRIMARY KEY NOT NULL AUTO_INCREMENT,
    bucket_tema_adm_instituto_id BIGINT(20) UNSIGNED NOT NULL,
    bucket_deficiencia_adm_id BIGINT(20) UNSIGNED NOT NULL,
    fallos INT,
    fallos_masculino INT,
    fallos_femenino INT,
    FOREIGN KEY(bucket_tema_adm_instituto_id) REFERENCES bucket_tema_adm_instituto(id),
    FOREIGN KEY(bucket_deficiencia_adm_id) REFERENCES bucket_deficiencia_adm(id)
);