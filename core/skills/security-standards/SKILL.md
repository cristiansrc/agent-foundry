---
name: security-standards
description: Estándares de seguridad para aplicaciones Spring Boot y Frontend. Usar para JWT, OAuth2/OIDC, Keycloak, RBAC, prevención de vulnerabilidades y gestión de identidad.
---

# Security Standards

Esta skill asegura que el código generado sea seguro por diseño.

## 1. Autenticación y Autorización
- **JWT:** Implementar rotación de tokens y validación estricta.
- **OAuth2/OIDC:** Preferir Authorization Code + PKCE para frontends y Client Credentials para comunicación service-to-service.
- **Keycloak:** Usar realms, clients, roles y scopes explícitos; no mezclar credenciales de admin con credenciales de aplicación.
- **RBAC:** Uso de `@PreAuthorize` con roles y permisos claros.
- **Secrets (Gitleaks Shield):** NUNCA hardcodear credenciales, API Keys o tokens en código o specs. Usar variables de entorno o Secret Managers. Todo commit debe pasar `gitleaks detect --staged` antes de realizarse.

## 2. OAuth2/OIDC con Keycloak
- **Issuer:** Validar siempre contra `issuer-uri`/discovery document del realm.
- **JWKS:** Verificar firma con JWKS remoto; no aceptar tokens sin `iss`, `aud`, `exp` y `typ` válidos.
- **Audience:** Exigir `aud` o `azp` esperado por la API; rechazar tokens emitidos para otro client.
- **Roles:** Mapear roles desde `realm_access.roles` o `resource_access.<client>.roles` de forma explícita.
- **Flows:** Deshabilitar flows no usados. Evitar Resource Owner Password Credentials salvo pruebas locales controladas.
- **Refresh tokens:** Mantenerlos fuera del frontend cuando sea posible; en SPA usar PKCE y sesiones cortas.
- **Logout:** Implementar logout OIDC y limpieza de sesión/cookies cuando aplique.

## 3. Protección de Datos
- **Validación de Input:** Validar todos los campos de entrada para prevenir Inyección SQL y XSS.
- **Sanitización:** Limpiar datos que se mostrarán en el frontend.
- **Sensibilidad:** No exponer datos sensibles en logs ni en respuestas de API (ej. passwords, tokens).

## 4. Configuración de Seguridad
- **CORS:** Configuración restrictiva basada en el entorno.
- **Headers:** Implementar headers de seguridad básicos (HSTS, Content-Security-Policy).
- **OWASP:** Seguir las recomendaciones del OWASP Top 10.

## 5. Checklist de Implementación
- Documentar realm, client IDs, roles, scopes, redirect URIs y audiences en la spec.
- Crear variables de entorno para issuer, client ID, client secret y audience.
- Agregar tests para token válido, token expirado, issuer incorrecto, audience incorrecto y rol insuficiente.
- En Spring Boot, usar Resource Server OAuth2 para APIs y validar autoridades con tests.
- En frontend, usar Authorization Code + PKCE y no guardar tokens en `localStorage` si se puede evitar.
