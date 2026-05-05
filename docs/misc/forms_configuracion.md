# Seguridad en los formularios propuesta

Los formularios son susceptibles puertas de entrada para posibles ataques. Como seguridad se puede establecer según lo aprendido:

## CSRF:

Token que va a junto a las cookies del usuario que establece un contrato. Deben de corresponder según la sesión. En caso de que no sea el mismo, la conexión no es válida y los envíos de formulario fallan.

## Turnstile:

Token tipo captcha que establece la conexión. Si no se envía con el formulario y luego se valida, el formulario no se recibe.

## Campo honeypot:

Campo invisible al usuario y lectores pero los bots que lean el HTML lo tratan de rellenar. En caso de que venga relleno, el formulario detecta que es un bot y cierra la conexión o desvía el envío de formulario.
