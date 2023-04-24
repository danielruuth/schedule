import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import PrimeVue from "primevue/config";
import Button from 'primevue/button'
import Dialog from 'primevue/dialog';
import DynamicDialog from 'primevue/dynamicdialog'
import DialogService from 'primevue/dialogservice'
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import ColumnGroup from 'primevue/columngroup';   // optional
import Row from 'primevue/row';                   // optional
import Calendar from 'primevue/calendar';
import InputSwitch from 'primevue/inputswitch'
import ContextMenu from 'primevue/contextmenu';
import Chip from 'primevue/chip';
import ProgressSpinner from 'primevue/progressspinner';
import ScrollPanel from 'primevue/scrollpanel';
import ColorPicker from 'primevue/colorpicker';
import Badge from 'primevue/badge';
import BadgeDirective from 'primevue/badgedirective';

//theme
import './assets/base.scss'
import "primevue/resources/themes/tailwind-light/theme.css";     
import "primevue/resources/primevue.min.css";
import "primeicons/primeicons.css";



const app = createApp(App)

//Services
app.use(router)
app.use(PrimeVue)
app.use(DialogService)

//Global components
app.component('Button', Button)
app.component('DynamicDialog', DynamicDialog)
app.component('DataTable', DataTable)
app.component('Column', Column)
app.component('ColumnGroup', ColumnGroup)
app.component('Row', Row)
app.component('Calendar', Calendar)
app.component('Dialog', Dialog)
app.component('InputSwitch', InputSwitch)
app.component('ContextMenu', ContextMenu)
app.component('Chip', Chip)
app.component('ProgressSpinner', ProgressSpinner)
app.component('ScrollPanel', ScrollPanel)
app.component('ColorPicker', ColorPicker)
app.component('Badge', Badge)
app.directive('Badge', BadgeDirective);

app.mount('#app')
