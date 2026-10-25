# 📁 Carpeta de Información - Trámite Claro

Esta carpeta contiene toda la información detallada de los trámites en formato JSON.

## Estructura

```
info/
├── tramites/          # Archivos JSON con información detallada de cada trámite
├── esquema.json       # Esquema de validación para los JSONs de trámites
└── README.md          # Este archivo
```

## Formato de Archivos JSON

Cada trámite tiene su propio archivo JSON con la siguiente estructura:

```json
{
  "id": "identificador-del-tramite",
  "nombre": "Nombre completo del trámite",
  "categoria": "Categoría del trámite",
  "duracion_estimada": "Tiempo aproximado",
  "dificultad": "baja|media|alta",
  "costo_aproximado": "Costo en pesos o dólares",
  "descripcion_simple": "Descripción breve y clara",
  "pasos": [
    {
      "numero": 1,
      "titulo": "Título del paso",
      "descripcion": "Explicación muy detallada (nivel primaria)",
      "tiempo_estimado": "Tiempo para este paso",
      "consejos": ["Consejo 1", "Consejo 2"],
      "documentos_requeridos": [
        {
          "nombre": "Nombre del documento",
          "tipo": "original|copia|digital",
          "descripcion": "Explicación simple del documento",
          "obligatorio": true,
          "cantidad": 1,
          "vigencia": "Requisitos de vigencia si aplica",
          "ejemplos": ["Ejemplo 1", "Ejemplo 2"]
        }
      ]
    }
  ],
  "checklist_completo": {
    "documentos_obligatorios": [],
    "documentos_opcionales": [],
    "recomendaciones_generales": []
  }
}
```

## Nivel de Detalle

Todas las explicaciones están escritas con un nivel de detalle como si se explicara a un niño de primaria:
- Lenguaje simple y claro
- Sin tecnicismos innecesarios
- Ejemplos concretos
- Explicaciones de términos oficiales

### Ejemplo:

❌ **Evitar**: "Identificación oficial con fotografía y firma autógrafa"

✅ **Usar**: "Necesitas una credencial oficial que diga quién eres. Debe tener tu foto y tu firma. Por ejemplo, tu INE (credencial para votar) o tu pasaporte. Debe ser la original, no una copia, y debe estar en buen estado, sin roturas."

## Trámites Documentados

1. visa-americana.json
2. visa-canada.json
3. pasaporte-primera-vez.json
4. pasaporte-renovacion.json
5. cambio-propietario-vehiculo.json
6. apostilla-documentos.json
7. residencia-temporal-mexico.json
8. licencia-conducir.json
9. acta-nacimiento.json
10. rfc-persona-fisica.json
11. escrituras-propiedad.json
12. testamento.json
13. permiso-menor-viajar.json
14. naturalizacion-mexicana.json
15. pension-adulto-mayor.json

## Uso

Estos archivos JSON se utilizan para:
1. Poblar la base de datos con información detallada
2. Mostrar pasos del proceso en la aplicación
3. Generar checklists personalizados para usuarios
4. Documentar requisitos específicos por paso

## Mantenimiento

Para agregar un nuevo trámite:
1. Crea un archivo JSON siguiendo el esquema
2. Usa nombres descriptivos en kebab-case
3. Asegúrate de incluir TODOS los pasos
4. Explica cada documento con mucho detalle
5. Agrega consejos útiles basados en experiencias reales
