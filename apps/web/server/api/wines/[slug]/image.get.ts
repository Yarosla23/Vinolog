export default defineEventHandler(async (event) => {
  const slug = getRouterParam(event, 'slug')
  if (!slug) {
    throw createError({
      statusCode: 400,
      message: 'Не указан slug вина.',
    })
  }

  const config = useRuntimeConfig()
  const target = `${config.retrievalBaseUrl}/v1/wines/${encodeURIComponent(slug)}/image`

  try {
    return await proxyRequest(event, target)
  }
  catch (error) {
    throw createError({
      statusCode: 502,
      message: 'Не удалось загрузить изображение вина.',
      cause: error,
    })
  }
})
