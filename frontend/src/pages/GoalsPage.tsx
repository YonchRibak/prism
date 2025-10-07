import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'

export const GoalsPage = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Financial Goals</h1>
          <p className="text-muted-foreground">
            Track your progress towards financial milestones
          </p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          New Goal
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {[
          {
            name: 'Emergency Fund',
            target: '$10,000',
            current: '$6,500',
            deadline: '2025-12-31',
            description: 'Build a 6-month emergency fund'
          },
          {
            name: 'Vacation Fund',
            target: '$3,000',
            current: '$1,200',
            deadline: '2025-08-15',
            description: 'Save for summer vacation'
          },
          {
            name: 'New Car',
            target: '$25,000',
            current: '$8,500',
            deadline: '2026-06-01',
            description: 'Down payment for new car'
          },
          {
            name: 'Home Renovation',
            target: '$15,000',
            current: '$4,200',
            deadline: '2025-10-31',
            description: 'Kitchen and bathroom remodel'
          },
        ].map((goal) => {
          const currentAmount = parseFloat(goal.current.replace('$', '').replace(',', ''))
          const targetAmount = parseFloat(goal.target.replace('$', '').replace(',', ''))
          const percentage = (currentAmount / targetAmount) * 100

          return (
            <Card key={goal.name}>
              <CardHeader>
                <CardTitle className="text-lg">{goal.name}</CardTitle>
                <CardDescription>{goal.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between text-sm">
                  <span>Current: {goal.current}</span>
                  <span>Target: {goal.target}</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-3">
                  <div
                    className="bg-primary h-3 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min(percentage, 100)}%` }}
                  />
                </div>
                <div className="flex justify-between text-sm text-muted-foreground">
                  <span>{percentage.toFixed(1)}% complete</span>
                  <span>Due: {new Date(goal.deadline).toLocaleDateString()}</span>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </motion.div>
  )
}