export default defineNuxtRouteMiddleware(() => {
  const config = useRuntimeConfig()
  if (config.public.sommelierMode === 'off') {
    return abortNavigation(createError({ statusCode: 404, statusMessage: 'Страница не найдена' }))
  }
})
