import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'

export const BudgetsPage = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Budgets</h1>
          <p className="text-muted-foreground">
            Set and track your spending limits
          </p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Create Budget
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {[
          { name: 'Monthly Budget', amount: '$3,500', spent: '$2,650', category: 'General' },
          { name: 'Food & Dining', amount: '$400', spent: '$320', category: 'Food' },
          { name: 'Transportation', amount: '$200', spent: '$150', category: 'Transport' },
          { name: 'Entertainment', amount: '$300', spent: '$180', category: 'Entertainment' },
        ].map((budget) => {
          const spentAmount = parseFloat(budget.spent.replace('$', '').replace(',', ''))
          const totalAmount = parseFloat(budget.amount.replace('$', '').replace(',', ''))
          const percentage = (spentAmount / totalAmount) * 100

          return (
            <Card key={budget.name}>
              <CardHeader>
                <CardTitle className="text-lg">{budget.name}</CardTitle>
                <CardDescription>{budget.category}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between text-sm">
                  <span>Spent: {budget.spent}</span>
                  <span>Budget: {budget.amount}</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      percentage > 90 ? 'bg-red-500' : percentage > 75 ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(percentage, 100)}%` }}
                  />
                </div>
                <p className="text-sm text-muted-foreground">
                  {percentage.toFixed(1)}% of budget used
                </p>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </motion.div>
  )
}