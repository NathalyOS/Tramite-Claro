-- Trámite Claro
-- Datos iniciales (seeds) para la tabla documentos.
-- Catálogo de documentos oficiales comunes con descripciones MUY detalladas en lenguaje simple.

USE tramite_claro;

-- DOCUMENTOS DE IDENTIFICACIÓN
INSERT INTO documentos (nombre, descripcion, tipo, vigencia, ejemplos, categoria) VALUES
('Identificación oficial vigente', 
'Es una credencial que dice quién eres y que está aprobada por el gobierno. Debe tener tu foto, tu firma y tu nombre completo. La puedes usar para demostrar que eres tú. Debe estar en buen estado, sin roturas ni manchas, y la fecha no debe haber pasado (no debe estar vencida).', 
'original', 
'Vigente, no vencida', 
'INE (credencial para votar), Pasaporte mexicano, Cédula profesional', 
'identificacion'),

('Copia de identificación oficial', 
'Es una fotocopia de tu identificación oficial. Debe verse claramente tu foto, tu nombre y todos los datos. La puedes hacer en cualquier papelería donde tengan copiadora. Es importante que se vea bien, no borrosa.', 
'copia', 
'Copia reciente de una identificación vigente', 
'Copia de INE, Copia de pasaporte, Copia de cédula profesional', 
'identificacion'),

('Pasaporte vigente', 
'Es tu libreta azul que sirve para viajar a otros países. Tiene tu foto, tus datos y un montón de páginas. Debe estar en buen estado y no debe estar vencido. La fecha de vencimiento viene en la página donde está tu foto.', 
'original', 
'Debe vencer al menos 6 meses después de tu viaje', 
'Pasaporte mexicano azul', 
'identificacion'),

('CURP impreso', 
'Es un papel que tiene 18 letras y números que son únicos para ti. Se llama Clave Única de Registro de Población. Lo puedes imprimir de internet en la página del gobierno. Debe verse bien, sin manchas.', 
'copia', 
'No tiene vencimiento, pero debe ser impresión reciente', 
'CURP actualizado con código QR', 
'identificacion');

-- COMPROBANTES DE DOMICILIO
INSERT INTO documentos (nombre, descripcion, tipo, vigencia, ejemplos, categoria) VALUES
('Comprobante de domicilio reciente', 
'Es un papel que demuestra dónde vives. Debe tener tu nombre completo y tu dirección exacta (calle, número, colonia, ciudad). Debe ser reciente, es decir, de hace poco tiempo. No debe tener más de 3 meses desde que lo recibiste.', 
'original', 
'No mayor a 3 meses', 
'Recibo de luz (CFE), Recibo de agua, Recibo de teléfono fijo, Estado de cuenta bancario, Recibo de predial', 
'comprobante'),

('Comprobante de domicilio (copia)', 
'Es una fotocopia de tu comprobante de domicilio. Debe verse claramente tu nombre, tu dirección y la fecha. La fecha debe ser reciente (no más de 3 meses).', 
'copia', 
'No mayor a 3 meses', 
'Copia de recibo de luz, agua o teléfono', 
'comprobante');

-- ACTAS DEL REGISTRO CIVIL
INSERT INTO documentos (nombre, descripcion, tipo, vigencia, ejemplos, categoria) VALUES
('Acta de nacimiento original', 
'Es el papel oficial que demuestra cuándo y dónde naciste. La emite el Registro Civil. Debe ser original (no fotocopia) y debe ser reciente. Tiene un sello con colores del gobierno y una firma.', 
'original', 
'No mayor a 6 meses para trámites oficiales', 
'Acta de nacimiento certificada del Registro Civil', 
'acta_civil'),

('Acta de nacimiento (copia certificada)', 
'Es una copia especial de tu acta de nacimiento que tiene el mismo valor que la original. La puedes pedir en el Registro Civil y tiene sellos oficiales. Es diferente a una simple fotocopia.', 
'copia_certificada', 
'No mayor a 6 meses para trámites oficiales', 
'Copia certificada del Registro Civil', 
'acta_civil'),

('Acta de matrimonio', 
'Es el papel oficial que dice que te casaste. Lo da el Registro Civil después de tu boda. Debe ser original o copia certificada, con sellos oficiales. Tiene la fecha de tu boda y los nombres de los dos.', 
'original', 
'Reciente si se usa para trámites oficiales', 
'Acta de matrimonio del Registro Civil', 
'acta_civil');

-- DOCUMENTOS FINANCIEROS
INSERT INTO documentos (nombre, descripcion, tipo, vigencia, ejemplos, categoria) VALUES
('Estado de cuenta bancario', 
'Es un papel que te da tu banco cada mes. Dice cuánto dinero tienes y qué movimientos has hecho. Sirve para demostrar que tienes dinero en el banco. Debe ser reciente (de hace poco).', 
'original', 
'No mayor a 3 meses', 
'Estado de cuenta de Bancomer, Santander, Banamex, HSBC', 
'financiero'),

('Comprobante de ingresos', 
'Es un papel que demuestra cuánto dinero ganas al mes. Puede ser un recibo de nómina si trabajas en una empresa, o una declaración si trabajas por tu cuenta. Debe ser reciente.', 
'original', 
'No mayor a 3 meses', 
'Recibo de nómina, Carta de ingresos, Declaración de impuestos', 
'financiero'),

('Constancia de situación fiscal', 
'Es un papel que puedes sacar de internet del SAT (el lugar de los impuestos). Dice tu RFC y tus datos fiscales. Es gratis y lo puedes imprimir tú mismo. Debe tener tu e.firma o sello digital.', 
'digital', 
'No mayor a 1 mes para trámites oficiales', 
'Constancia del SAT con código QR', 
'fiscal');

-- DOCUMENTOS FISCALES
INSERT INTO documentos (nombre, descripcion, tipo, vigencia, ejemplos, categoria) VALUES
('RFC (Registro Federal de Contribuyentes)', 
'Es una tarjeta o papel que tiene tu clave de impuestos. Son 13 letras y números que te identifican con el SAT (la oficina de impuestos). Lo necesitas para trabajar y para hacer trámites oficiales.', 
'original', 
'No tiene vencimiento', 
'Cédula de RFC, Constancia de situación fiscal', 
'fiscal'),

('Copia de RFC', 
'Es una fotocopia de tu tarjeta o cédula de RFC. Debe verse claramente tu nombre, tu clave RFC (las 13 letras y números) y el código de barras si tiene.', 
'copia', 
'Copia reciente', 
'Copia de cédula de RFC', 
'fiscal');

-- DOCUMENTOS VEHICULARES
INSERT INTO documentos (nombre, descripcion, tipo, vigencia, ejemplos, categoria) VALUES
('Tarjeta de circulación', 
'Es la tarjeta oficial de tu carro o moto. Dice de qué marca y modelo es, de qué color, las placas que tiene y quién es el dueño. Debe estar vigente (no vencida) y en buen estado.', 
'original', 
'Vigente, no vencida', 
'Tarjeta de circulación del vehículo', 
'vehicular'),

('Factura del vehículo', 
'Es el papel que demuestra que compraste el carro. Dice cuánto pagaste y quién te lo vendió. Si es carro nuevo, es una factura de la agencia. Si es usado, puede ser un contrato de compraventa.', 
'original', 
'Debe corresponder al vehículo actual', 
'Factura original, Contrato de compraventa', 
'vehicular'),

('Placas del vehículo', 
'Son las placas de metal con números y letras que van en el frente y atrás de tu carro. Deben estar en buen estado y corresponder a lo que dice tu tarjeta de circulación.', 
'original', 
'Vigentes, no vencidas', 
'Placas metálicas del vehículo', 
'vehicular');

-- DOCUMENTOS NOTARIALES
INSERT INTO documentos (nombre, descripcion, tipo, vigencia, ejemplos, categoria) VALUES
('Carta poder', 
'Es un papel donde tú le das permiso a otra persona para hacer algo en tu nombre. Debe estar firmada por ti, por la persona a quien le das el poder, y por testigos. También puede ser firmada ante notario.', 
'original', 
'Depende del tipo de trámite', 
'Carta poder simple, Carta poder notariada', 
'notarial'),

('Escrituras de propiedad', 
'Son los papeles oficiales que demuestran que una casa o terreno es tuyo. Los hace un notario público y tienen muchos sellos y firmas. Son papeles muy importantes que debes guardar bien.', 
'original', 
'No tienen vencimiento', 
'Escritura pública de propiedad, Título de propiedad', 
'notarial');

-- DOCUMENTOS EDUCATIVOS
INSERT INTO documentos (nombre, descripcion, tipo, vigencia, ejemplos, categoria) VALUES
('Certificado de estudios', 
'Es un papel oficial que dice qué estudiaste y qué calificaciones sacaste. Puede ser de primaria, secundaria, preparatoria o universidad. Debe tener el sello de la escuela y la firma del director.', 
'original', 
'Dependiendo del uso, puede necesitar apostilla', 
'Certificado de primaria, secundaria, preparatoria, universidad', 
'educativo'),

('Título profesional', 
'Es el papel oficial que dice que terminaste una carrera universitaria. Lo da la universidad y tiene tu nombre, el nombre de la carrera y la fecha. Tiene sellos y firmas oficiales.', 
'original', 
'No tiene vencimiento', 
'Título universitario, Cédula profesional', 
'educativo');

-- FOTOGRAFÍAS
INSERT INTO documentos (nombre, descripcion, tipo, vigencia, ejemplos, categoria) VALUES
('Fotografía tamaño infantil', 
'Es una foto tuya del tamaño de una estampilla chiquita. Debe ser reciente (que te parezcas), a color, con fondo blanco. Debes estar de frente, sin lentes oscuros y sin sonreír mucho. Mide aproximadamente 2.5 x 3 cm.', 
'original', 
'Reciente (no mayor a 6 meses)', 
'Foto tamaño infantil o credencial', 
'fotografia'),

('Fotografía tamaño pasaporte', 
'Es una foto tuya un poco más grande que la infantil. Debe ser reciente, a color, con fondo blanco. Debes estar de frente mirando a la cámara. Mide aproximadamente 3.5 x 4.5 cm.', 
'original', 
'Reciente (no mayor a 6 meses)', 
'Foto tamaño pasaporte', 
'fotografia');

-- DOCUMENTOS MÉDICOS
INSERT INTO documentos (nombre, descripcion, tipo, vigencia, ejemplos, categoria) VALUES
('Certificado médico', 
'Es un papel donde un doctor dice que estás sano y que puedes hacer cierta actividad. El doctor te revisa y luego firma el papel. Debe tener el sello del doctor y su firma.', 
'original', 
'No mayor a 3 meses generalmente', 
'Certificado médico general, Certificado de salud', 
'medico');

-- DOCUMENTOS LABORALES
INSERT INTO documentos (nombre, descripcion, tipo, vigencia, ejemplos, categoria) VALUES
('Carta de trabajo', 
'Es un papel que hace tu jefe o la empresa donde trabajas. Dice desde cuándo trabajas ahí, en qué puesto y cuánto ganas. Debe tener el sello de la empresa y la firma de tu jefe o de recursos humanos.', 
'original', 
'No mayor a 3 meses', 
'Carta de empleado, Constancia laboral', 
'laboral');
