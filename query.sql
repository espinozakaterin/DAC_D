SELECT PKUsuario, Nombre, Apellido, Usuario, Contrasena, Estado FROM usuarios WHERE Usuario LIKE '%PASANTE%';
SELECT PKUsuario, Nombre, Apellido, Usuario, Contrasena, Estado FROM usuarios WHERE Nombre LIKE '%PASANTE%';
SELECT PKUsuario, Nombre, Apellido, Usuario, Contrasena, Estado FROM usuarios ORDER BY PKUsuario DESC LIMIT 20;
