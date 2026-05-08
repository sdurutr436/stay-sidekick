# Activar superadmin

Tras ejecutar la migración `e5f6a7b8c9d0_add_es_superadmin_to_usuarios.py`,
ejecutar la siguiente consulta SQL en la base de datos de producción para
activar el superadmin:

```sql
UPDATE usuarios
SET es_superadmin = true
WHERE email = '<tu_email>';
```

El superadmin puede:
- Ver y gestionar usuarios de cualquier empresa desde /gestion-usuarios
- Seleccionar la empresa activa con el selector que aparece en la parte superior
- Usar el endpoint GET /api/empresas para obtener la lista de empresas

Nota: el nuevo token JWT incluye el claim `es_superadmin: true`. El usuario
debe cerrar sesión y volver a entrar después de aplicar el cambio en la BD
para que el flag tenga efecto.
