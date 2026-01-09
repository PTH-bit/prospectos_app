// Funciones de filtrado de fechas para el panel de prospectos

function filtrarHoy() {
    const hoy = new Date().toISOString().split('T')[0];
    document.getElementById('fecha_inicio').value = hoy;
    document.getElementById('fecha_fin').value = hoy;
    document.getElementById('formFiltroFechas').submit();
}

function filtrarSemana() {
    const hoy = new Date();
    const primerDia = new Date(hoy);
    primerDia.setDate(hoy.getDate() - hoy.getDay());

    const ultimoDia = new Date(primerDia);
    ultimoDia.setDate(primerDia.getDate() + 6);

    document.getElementById('fecha_inicio').value = primerDia.toISOString().split('T')[0];
    document.getElementById('fecha_fin').value = ultimoDia.toISOString().split('T')[0];
    document.getElementById('formFiltroFechas').submit();
}

function filtrarMes() {
    const hoy = new Date();
    const primerDia = new Date(hoy.getFullYear(), hoy.getMonth(), 1);
    const ultimoDia = new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0);

    document.getElementById('fecha_inicio').value = primerDia.toISOString().split('T')[0];
    document.getElementById('fecha_fin').value = ultimoDia.toISOString().split('T')[0];
    document.getElementById('formFiltroFechas').submit();
}

function filtrarTrimestre() {
    const hoy = new Date();
    const mesActual = hoy.getMonth();
    const primerMesTrimestre = Math.floor(mesActual / 3) * 3;

    const primerDia = new Date(hoy.getFullYear(), primerMesTrimestre, 1);
    const ultimoDia = new Date(hoy.getFullYear(), primerMesTrimestre + 3, 0);

    document.getElementById('fecha_inicio').value = primerDia.toISOString().split('T')[0];
    document.getElementById('fecha_fin').value = ultimoDia.toISOString().split('T')[0];
    document.getElementById('formFiltroFechas').submit();
}

function filtrarAnio() {
    const hoy = new Date();
    const primerDia = new Date(hoy.getFullYear(), 0, 1);
    const ultimoDia = new Date(hoy.getFullYear(), 11, 31);

    document.getElementById('fecha_inicio').value = primerDia.toISOString().split('T')[0];
    document.getElementById('fecha_fin').value = ultimoDia.toISOString().split('T')[0];
    document.getElementById('formFiltroFechas').submit();
}
