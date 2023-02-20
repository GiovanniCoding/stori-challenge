# Prueba Técnica para Stori

Para realizar la ejecución, es necesario únicamente de docker y docker compose.

Para esto solo hace falta ejecutar

```python
docker-compose up -d
```

Durante la ejecución se llevaran a cabo los siguientes pasos
1. Inicialización de la base de datos.
2. Lectura y procesamiento del archivo
3. Inserción en la base de datos de las transacciones del archivo csv
4. envío por correo de la información procesada al correo: fernando.yanez@storicard.com