import { isFeatureEnabled } from '#shared/utils/feature-flags'

export default defineNuxtRouteMiddleware(() => {
  const config = useRuntimeConfig()

  if (!isFeatureEnabled(config.public.astroEnabled)) {
    return navigateTo('/', { replace: true })
  }
})
