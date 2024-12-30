<template>
    <div v-html="renderedMarkdown"></div>
</template>

<script>
import { marked } from 'marked'

export default {
  props: ['text'],
  computed: {
    renderedMarkdown() {
      return marked(this.text || '')
    }
  }
}
</script>