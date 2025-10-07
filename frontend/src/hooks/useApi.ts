import { useState, useEffect } from 'react'

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

interface UseApiOptions {
  immediate?: boolean
}

export function useApi<T>(
  apiCall: () => Promise<T>,
  dependencies: React.DependencyList = [],
  options: UseApiOptions = { immediate: true }
): UseApiState<T> & { refetch: () => Promise<void> } {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null
  })

  const fetchData = async () => {
    setState(prev => ({ ...prev, loading: true, error: null }))

    try {
      const result = await apiCall()
      setState({ data: result, loading: false, error: null })
    } catch (error: any) {
      setState({
        data: null,
        loading: false,
        error: error.response?.data?.detail || error.message || 'An error occurred'
      })
    }
  }

  useEffect(() => {
    if (options.immediate) {
      fetchData()
    }
  }, dependencies)

  return {
    ...state,
    refetch: fetchData
  }
}

// Specialized hooks for common operations
export function useAccounts() {
  return useApi(async () => {
    const { accountService } = await import('@/services')
    return accountService.getAccounts()
  })
}

export function useTransactions(filters?: any) {
  return useApi(async () => {
    const { transactionService } = await import('@/services')
    return transactionService.getTransactions(filters)
  }, [filters])
}

export function useCategories() {
  return useApi(async () => {
    const { categoryService } = await import('@/services')
    return categoryService.getCategories()
  })
}

export function useBudgets() {
  return useApi(async () => {
    const { budgetService } = await import('@/services')
    return budgetService.getBudgets()
  })
}

export function useGoals() {
  return useApi(async () => {
    const { goalService } = await import('@/services')
    return goalService.getGoals()
  })
}