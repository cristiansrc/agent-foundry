---
name: keycloak-standard
description: Estándares y mejores prácticas para la configuración y gestión de identidad con Keycloak.
---

# Estándares Keycloak

Guía para la implementación segura y escalable de IAM (Identity and Access Management) con Keycloak.

## Arquitectura de Realms y Clientes
- **Realms**: Usar un Realm por aplicación o por entorno (Desarrollo, QA, Producción). Evitar el uso del realm `master` para aplicaciones.
- **Clientes**: 
    - `Public`: Para Single Page Applications (SPA) y aplicaciones móviles (usan PKCE).
    - `Confidential`: Para aplicaciones Server-side (usan Client Secret).
    - `Bearer-only`: Para microservicios que solo validan tokens.

## Seguridad y Flujos de Autenticación
- **Flujo Estándar**: Usar siempre `Authorization Code Flow` con `PKCE`.
- **Tokens**: 
    - Mantener un `Access Token Lifespan` corto (ej: 5-15 min).
    - Usar `Refresh Tokens` para sesiones largas.
- **HTTPS**: Keycloak DEBE ejecutarse siempre tras HTTPS en producción.

## Roles y Autorización (RBAC/ABAC)
- **Roles de Realm**: Para permisos globales (ej: `admin`, `user`).
- **Roles de Cliente**: Para permisos específicos de una aplicación.
- **Grupos**: Usar para organizar usuarios jerárquicamente y asignar roles masivamente.
- **Client Scopes**: Usar para definir claims comunes (ej: `profile`, `email`, `roles`) que se comparten entre clientes.

## Gestión de Usuarios y Federación
- **User Federation**: Conectar con LDAP/Active Directory para gestión de identidades corporativas.
- **Identity Brokering**: Usar para permitir login social (Google, GitHub) o protocolos OIDC/SAML externos.
- **Mappers**: Usar Protocol Mappers para añadir claims personalizados al token (ej: `organization_id`).

## Operaciones y Mejores Prácticas
- **Configuración como Código**: Exportar la configuración del realm a JSON y versionarla. Usar herramientas como Terraform o `keycloak-config-cli`.
- **Base de Datos**: Usar una base de datos externa (PostgreSQL recomendada) para persistencia.
- **Temas (Themes)**: Personalizar la página de login mediante temas para mantener la identidad visual de la marca.
- **Observabilidad**: Habilitar métricas y logs en formato JSON para integración con stacks de monitoreo.
