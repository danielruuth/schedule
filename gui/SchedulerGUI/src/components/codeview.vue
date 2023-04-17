<template>
    <div class="code-view--wrapper">
        <code><pre><span v-html="syntaxed"></span></pre></code>
    </div>
</template>
<script setup>
    import {syntaxHighlight} from '../plugins/syntax-highlite';
    const props = defineProps({
        code:Object
    })

    const syntaxed = syntaxHighlight(JSON.stringify(props.code.value, undefined, 2));
</script>
<style lang="scss">
.code-view--wrapper{
    border-radius: 4px;
    background-color: rgba(41,45,62,1);
    font-size: 12px;
    color: #89DDFF;
    
    pre {
        padding: 5px;
    }
    .string {
    color: #C3E88D;
    }
    .number {
    color: #F78C6C;
    }
    .boolean {
    color: #F78C6C;
    }
    .null {
    color: magenta;
    }
    .key {
    color: #F07178;
    }
}
</style>