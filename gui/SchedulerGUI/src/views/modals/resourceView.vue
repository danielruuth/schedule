<script setup>
    import {ref, inject} from 'vue'
   
    const dialogRef = inject('dialogRef')
    const emit = defineEmits(['AddedResources'])

    const resources = ref(dialogRef.value.data.resources)
    const resource_name = ref()

    const addResource = function(){
        resources.value.push(
            {
                name: resource_name.value
            }
        )
        resource_name.value = ''
        emit('AddedResources', resources)
    }
    const removeResource = function(index){
        console.log(index)
        resources.value.splice(index,1)


        emit('AddedResources', resources)

        
    }
    const onCellEditComplete = function (event){
        if(event.newValue != event.value){
            console.log(event)
            resources.value[event.index] = { name: event.newValue }
            emit('AddedResources', resources)
        }
    }
</script>
<template>
    <div class="grid gap-1 grid-cols-10 gap-x-2">
        <div class="col-span-9">
            <span class="text-xs font-bold uppercase">Namn </span><small class="text-xs font-light">t.ex Daniel</small>
            <input type="text" v-model="resource_name" class="form-input rounded-md bg-gray-100 border-transparent w-full" />
        </div>
        <div class="col-span-1">
            <span class="text-xs font-bold uppercase">&nbsp;</span><br />
            <Button label="+" class="w-full float-right" style="height:42px" @click="addResource()" />
        </div>
        <div class="col-span-10">
            <span class="text-xs font-bold uppercase">Resurser </span>
            <DataTable :value="resources" class="p-datatable-sm" editMode="cell" @cell-edit-complete="onCellEditComplete" scrollable scrollHeight="200px">
                <Column field="name" header="Resurs">
                    <template #editor="{ data, field }">
                        <input type="text" v-model="data[field]" class="form-input rounded-md bg-gray-100 border-transparent w-full" autofocus />    
                    </template>
                </Column>
                <Column style="width:65px">
                    <template #body="{index}">
                        <Button icon="pi pi-trash" plain text rounded aria-label="Radera" @click="removeResource(index)"/>    
                    </template>
                </Column>
            </DataTable>
        </div>
    </div>
</template>