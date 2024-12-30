<template>
  <div>
    <MarkdownWrapper :text="text"/>
  </div>
</template>

<script>
import MarkdownWrapper from './MarkdownWrapper.vue';
import axios from 'axios'

const POLL_INTERVAL = 250

export default {
  components: {
    MarkdownWrapper
  },
  data() {
    return {
      text: null,
      intervalId: null
    }
  },
  created() {
    // Fetch data right away
    this.fetchText()

    this.intervalId = setInterval(() => {
      this.fetchText()
    }, POLL_INTERVAL)
  },
  beforeUnmount() {
    if (this.intervalId) {
      clearInterval(this.intervalId)
    }
  },
  methods: {
    async fetchText() {
      try {
        const response = await axios.get('http://127.0.0.1:5000/analysis')
        this.text = response.data.content[0].text
      } catch (error) {
        console.error('Error fetching data:', error)
      }
    }
  }
}
</script>
