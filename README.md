# multiMaquinaGervasi
Estimado,

Se presenta a continuación la documentación técnica formal del sistema de optimización granulométrica desarrollado, incluyendo su arquitectura matemática, estructural y de despliegue en infraestructura cloud.

---

1. OBJETIVO DEL SISTEMA

Desarrollar una plataforma digital capaz de:

* Analizar curvas granulométricas reales.
* Compararlas con curvas objetivo normativas.
* Minimizar automáticamente la desviación global.
* Corregir variaciones locales entre tamices.
* Generar recomendaciones técnicas e informes automáticos.
* Permitir acceso remoto y gestión multiusuario.

---

2. FORMULACIÓN MATEMÁTICA

El sistema resuelve el siguiente problema de optimización con restricciones:

Minimizar:

```
min_w  error(mezcla, curva_objetivo)
```

Sujeto a:

```
Σ w_i = 1  
0 ≤ w_i ≤ 1  
```

Donde:

* w_i son las proporciones de cada material.
* La mezcla es la combinación lineal de curvas individuales.
* La función error corresponde al error cuadrático medio respecto a la curva objetivo.

Este problema no tiene solución analítica cerrada y requiere optimización numérica formal.

---

3. MOTOR DE OPTIMIZACIÓN

Se implementa el algoritmo SLSQP (Sequential Least Squares Programming):

* Optimización multivariable con restricciones.
* Garantiza cumplimiento físico (100% total).
* Impide valores negativos o superiores al límite.
* Converge al mínimo error posible respetando las condiciones físicas.

El sistema:

* Parte de una combinación inicial.
* Evalúa el error respecto a la curva ideal.
* Ajusta iterativamente las proporciones.
* Minimiza desviaciones globales y locales entre tamices consecutivos.

---

4. CORRECCIÓN DE VARIACIONES GRANULOMÉTRICAS

Además de minimizar el error global, el sistema:

* Detecta desviaciones individuales por tamiz.
* Identifica excesos o déficits.
* Reduce discontinuidades entre tamaños consecutivos.
* Analiza zonas granulométricas (gruesos, medios y finos).
* Genera mezclas complementarias para compensar déficits específicos.

---

5. NORMALIZACIÓN Y EXPANSIÓN DE CURVAS

* Curvas objetivo definidas en 9 puntos normativos.
* Expansión automática a tamices reales mediante interpolación logarítmica.
* Alineación automática de curvas reales al set master de tamices.
* Adaptación dinámica a diferentes configuraciones de planta.

---

6. ARQUITECTURA DEL SISTEMA

Estructura modular:

* Backend en Flask con Blueprints organizados por dominio.
* Separación en capas: controller, model, utils.
* Gestión de autenticación y sesiones de usuario.
* Persistencia en base de datos estructurada por entidad industrial.

Frontend:

* Visualización comparativa de curvas.
* Generación automática de informes.
* Módulos independientes por funcionalidad (mezclas, mallas, componentes, usuarios).

---

7. CONTENERIZACIÓN Y DESPLIEGUE EN AWS

El sistema se encuentra dockerizado e incluye:

* Dockerfile para construcción reproducible del entorno.
* Separación de dependencias mediante requirements.txt.
* Variables de entorno gestionadas mediante archivo .env.
* Exposición controlada de puertos.

Infraestructura AWS:

* Despliegue en instancia EC2.
* Publicación mediante mapeo de puertos.
* Acceso remoto multiusuario.
* Reinicio automático del contenedor con política “unless-stopped”.
* Aislamiento del entorno respecto al sistema operativo base.

---

8. INTEGRACIÓN CONTINUA (CI)

Se implementa flujo de integración continua:

* Control de versiones mediante Git.
* Versionado estructurado de ramas.
* Automatización de despliegue mediante pipeline.
* Construcción automática de imagen Docker.
* Actualización remota del contenedor en servidor AWS.

Esto garantiza:

* Reproducibilidad del entorno.
* Reducción de errores manuales.
* Trazabilidad de cambios.
* Capacidad de rollback ante fallos.

---

9. COMPLEJIDAD APLICADA

El sistema integra simultáneamente:

* Optimización numérica con restricciones.
* Interpolación logarítmica.
* Minimización multivariable.
* Análisis granulométrico zonal.
* Arquitectura web modular.
* Contenerización.
* Infraestructura cloud.
* Integración continua.

No se trata de un cálculo aislado ni de un script experimental, sino de una solución estructurada de ingeniería computacional aplicada a un entorno industrial real.

---

