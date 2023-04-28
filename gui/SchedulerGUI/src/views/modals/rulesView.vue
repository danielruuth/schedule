<script setup>
    import {ref, inject} from 'vue'
    const dialogRef = inject('dialogRef')
    const emit = defineEmits(['UpdateRules'])

    const showAdvanced = ref(false)

    const health = ref(dialogRef.value.data.rules.health || false)
    const groupOffshift = ref(dialogRef.value.data.rules.group_offshift || false)
    const weekendsConcat = ref(dialogRef.value.data.rules.min_weekends || false)
    const availableShifts = ref(dialogRef.value.data.shifts || [])
    const custom_rules = ref(dialogRef.value.data.rules.custom_rules || [])


    const adv_name = ref()
    const adv_shift = ref('null')
    const adv_type = ref('nuöö')
    const adv_constraint = ref([0,0,0,0,0,0])

    
    const updateSettings = function(event){
        emit('UpdateRules', {'health': health, 'min_weekends': false, 'group_offshift': groupOffshift, 'custom_rules': custom_rules.value})
    }

    const addRule = function(){
        let newRule = {
            name: adv_name.value,
            shift: adv_shift.value,
            type: adv_type.value,
            constraints: adv_constraint.value
        }

        custom_rules.value.push(newRule)

        adv_name.value = ''
        adv_shift.value = 'null'
        adv_type.value = 'null'
        adv_constraint.value = [0,0,0,0,0,0]
        updateSettings()
    }

    const hint = ref()
    const example = ref()

    const updateHint = function(){
        
    }

</script>
<template>
    <div v-if="!showAdvanced" class="grid gap-1 gap-y-4 grid-cols-10 gap-x-2">
        <div class="col-span-5">
            <span class="text-xs font-bold uppercase">Används hälsoschema </span><br />
            <span class="text-xs font-light">Sätt regler efter hälsoschema-modellen, läs mer <a href="https://skr.se/skr/arbetsgivarekollektivavtal/arbetstid/dygnsvila.68896.html">här</a>.</span><br />
            <InputSwitch class="mt-4" v-model="health" @change="updateSettings($event)"/>
        </div>
        <div class="col-span-5">
            <span class="text-xs font-bold uppercase">Sammanhängande ledighet</span><br />
            <span class="text-xs font-light">Ha alltid två dagars sammanhållande ledighet</span><br />
            <InputSwitch class="mt-4" v-model="groupOffshift" @change="updateSettings($event)" />
        </div>
        <div class="col-span-4 col-start-4">
            <Button label="Avancerade inställningar" text class="w-full" @click="showAdvanced=true;"/>
        </div>
    </div>
    <div v-if="showAdvanced" class="grid gap-1 gap-y-4 grid-cols-10 gap-x-2">
        <div class="col-span-10 flex align-middle items-center">
            <Button text rounded @click="showAdvanced=false" icon="pi pi-arrow-left" />
            <span class="font-bold text-sm">Tillbaka</span>
        </div>
        <div class="col-span-10">
            <span class="text-sm font-bold capitalize">Skapa egen regel <small class="font-thin">(Avancerad nivå)</small></span>
        </div>
        <div class="col-span-5">
            <span class="font-bold text-xs">Namn <small class="font-thin">T.ex &quot;Begränsa verksamhetstid&quot;</small></span>
            <input type="text" v-model="adv_name" class="form-input rounded-md bg-gray-100 border-transparent w-full"/>
        </div>
        <div class="col-span-5">
            <span class="font-bold text-xs">Typ</span>
            <select name="shift" v-model="adv_type" class="form-input rounded-md bg-gray-100 border-transparent w-full" @change="updateHint()">
                <option value="null" selected>Välj</option>
                
                <option value="penalized_transitions">Straffade övergångar</option>
                <option value="weekly_sum_constraint">Begränsning veckototalsumma</option>
                <option value="shift_constraint">Begränsning per skift</option>
            </select>
        </div>

        <div class="col-span-5">
            <span class="font-bold text-xs capitalize">Förklaring</span>
            {{ hint }}
        </div>
        <div class="col-span-5">
            <span class="font-bold text-xs capitalize">Exempel</span>
            {{ example }}
        </div>

        <div class="col-span-4">
            <span class="font-bold text-xs">Skift</span>
            <select name="shift" v-model="adv_shift" class="form-input rounded-md bg-gray-100 border-transparent w-full">
                <option value="null" selected>Välj</option>
                <option value="offshift">Ledighet</option>
                <option v-for="(shift,index) in availableShifts" :value="index">{{ shift.name }}</option>
            </select>
        </div>
        <div class="col-span-2">
            <span class="font-bold text-xs">Hårt min.</span>
            <input type="number" name="soft_min" v-model="adv_constraint[0]" class="form-input rounded-md bg-gray-100 border-transparent w-full"/>
        </div>
        <div class="col-span-2">
            <span class="font-bold text-xs">Mjukt min.</span>
            <input type="number" name="soft_min" v-model="adv_constraint[1]" class="form-input rounded-md bg-gray-100 border-transparent w-full" />
        </div>
        <div class="col-span-2">
            <span class="font-bold text-xs">Överträdelse min</span>
            <input type="number" name="soft_min" v-model="adv_constraint[2]" class="form-input rounded-md bg-gray-100 border-transparent w-full" />
        </div>
        <div class="col-span-4"></div>
        <div class="col-span-2">
            <span class="font-bold text-xs">Hårt max.</span>
            <input type="number" name="soft_min" v-model="adv_constraint[3]" class="form-input rounded-md bg-gray-100 border-transparent w-full" />
        </div>
        <div class="col-span-2">
            <span class="font-bold text-xs">Mjukt max.</span>
            <input type="number" name="soft_min" v-model="adv_constraint[4]" class="form-input rounded-md bg-gray-100 border-transparent w-full" />
        </div>
        <div class="col-span-2">
            <span class="font-bold text-xs">Överträdelse max</span>
            <input type="number" name="soft_min" v-model="adv_constraint[5]" class="form-input rounded-md bg-gray-100 border-transparent w-full" />
        </div>
        <div class="col-span-4 col-start-7">
            <span class="font-bold text-xs">&nbsp; </span>
            <Button label="Lägg till avancerad regel" class="w-full" @click="addRule()" />
        </div>
        <div class="col-span-10 mt-8">
            <span class="text-sm font-bold capitalize">Regler</span>
            <DataTable :value="custom_rules">
                <Column field="name" header="Namn"></Column>
                <Column field="shift" header="Skift"></Column>
                <Column field="type" header="Typ"></Column>
                <Column field="constraints" header="Regler"></Column>
            </DataTable>
        </div>
    </div>
</template>