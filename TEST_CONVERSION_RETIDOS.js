/**
 * SCRIPT DE TESTEO PARA CONVERSIÓN RETIDOS → PASANTES
 * 
 * Ejecutar en la consola de auditoria.html (F12) para verificar las funciones
 * Compara CASO 1 (pasantes directos) vs CASO 2 (retidos múltiples)
 */

console.log('='.repeat(80));
console.log('TEST: Conversión Retidos → Pasantes');
console.log('='.repeat(80));

// ========= CASO 1: Una tabla con PASANTES (lo que ya funcionaba) =========
console.log('\n[CASO 1] Una tabla con PASANTES DIRECTOS');
console.log('-'.repeat(80));

const caso1_localStorage = [
  {
    mezclaId: "mezcla-0",
    nombre: "difucion 1",
    filas: [
      {tamiz: "9.5", porcentaje: "99.2"},
      {tamiz: "6.3", porcentaje: "76.6"},
      {tamiz: "4.8", porcentaje: "35.2"},
      {tamiz: "2.4", porcentaje: "12.4"},
      {tamiz: "1.2", porcentaje: "6.5"},
      {tamiz: "0.6", porcentaje: "4.7"},
      {tamiz: "0.3", porcentaje: "1.4"},
      {tamiz: "0.15", porcentaje: "0"}
    ]
  }
];

localStorage.setItem('tablasCargadas', JSON.stringify(caso1_localStorage));
const resultado1 = cargarDatosDelStorage();
console.log('✅ Resultado CASO 1:', resultado1);
console.log('   - Pasante: ' + resultado1.pasante_real.map(p => p.toFixed(1)).join(', '));

// ========= CASO 2: Múltiples tablas con RETIDOS (nuevo) =========
console.log('\n[CASO 2] Múltiples tablas con RETIDOS INDIVIDUALES');
console.log('-'.repeat(80));

const caso2_localStorage = [
  {
    mezclaId: "mezcla-0",
    nombre: "difucion 1",
    filas: [
      {tamiz: "9.5", porcentaje: "3.9"},
      {tamiz: "6.3", porcentaje: "28.5"},
      {tamiz: "4.8", porcentaje: "24.88"},
      {tamiz: "2.4", porcentaje: "42.64"},
      {tamiz: "1.2", porcentaje: "0"},
      {tamiz: "0.6", porcentaje: "0"},
      {tamiz: "0.3", porcentaje: "0"},
      {tamiz: "0.15", porcentaje: "0"}
    ]
  },
  {
    mezclaId: "mezcla-1",
    nombre: "difucion 2",
    filas: [
      {tamiz: "9.5", porcentaje: "0"},
      {tamiz: "6.3", porcentaje: "0"},
      {tamiz: "4.8", porcentaje: "0"},
      {tamiz: "2.4", porcentaje: "0"},
      {tamiz: "1.2", porcentaje: "100"},
      {tamiz: "0.6", porcentaje: "0"},
      {tamiz: "0.3", porcentaje: "0"},
      {tamiz: "0.15", porcentaje: "0"}
    ]
  },
  {
    mezclaId: "mezcla-2",
    nombre: "difucion 3",
    filas: [
      {tamiz: "9.5", porcentaje: "0"},
      {tamiz: "6.3", porcentaje: "0"},
      {tamiz: "4.8", porcentaje: "0"},
      {tamiz: "2.4", porcentaje: "0"},
      {tamiz: "1.2", porcentaje: "0"},
      {tamiz: "0.6", porcentaje: "32.6"},
      {tamiz: "0.3", porcentaje: "45.33"},
      {tamiz: "0.15", porcentaje: "22.07"}
    ]
  }
];

localStorage.setItem('tablasCargadas', JSON.stringify(caso2_localStorage));
const resultado2 = cargarDatosDelStorage();
console.log('✅ Resultado CASO 2:', resultado2);
console.log('   - Pasante: ' + resultado2.pasante_real.map(p => p.toFixed(1)).join(', '));

// ========= VERIFICACIONES =========
console.log('\n' + '='.repeat(80));
console.log('VERIFICACIONES:');
console.log('='.repeat(80));

console.log('\n✓ CASO 1 (pasantes directos):');
console.log('  - Longitud: ' + resultado1.pasante_real.length + ' tamices');
console.log('  - Primer valor: ' + resultado1.pasante_real[0].toFixed(1) + '% (debe ser ≈100)');
console.log('  - Último valor: ' + resultado1.pasante_real[resultado1.pasante_real.length-1].toFixed(1) + '% (debe ser ≈0)');
console.log('  - Monotonía: ' + (esDecreciente(resultado1.pasante_real) ? '✅ OK (decrece)' : '❌ FALLA'));

console.log('\n✓ CASO 2 (múltiples retidos):');
console.log('  - Longitud: ' + resultado2.pasante_real.length + ' tamices');
console.log('  - Primer valor: ' + resultado2.pasante_real[0].toFixed(1) + '% (debe ser ≈100)');
console.log('  - Último valor: ' + resultado2.pasante_real[resultado2.pasante_real.length-1].toFixed(1) + '% (debe ser ≈0)');
console.log('  - Monotonía: ' + (esDecreciente(resultado2.pasante_real) ? '✅ OK (decrece)' : '❌ FALLA'));

function esDecreciente(arr) {
  for (let i = 1; i < arr.length; i++) {
    if (arr[i] > arr[i-1]) return false;
  }
  return true;
}

console.log('\n' + '='.repeat(80));
console.log('🎯 TEST COMPLETADO');
console.log('='.repeat(80));
console.log('\nPróximos pasos:');
console.log('1. Clica "📋 Usar ejemplo" en la página');
console.log('2. Verifica que carga los datos correctamente');
console.log('3. Da clic en "📤 Ejecutar Auditoría"');
console.log('4. Si funciona, los datos están listos para el backend');
