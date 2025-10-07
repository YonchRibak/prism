import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'

export const AccountsPage = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Accounts</h1>
          <p className="text-muted-foreground">
            Manage your financial accounts
          </p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Add Account
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[
          { name: 'Checking Account', balance: '$2,345.67', type: 'Checking' },
          { name: 'Savings Account', balance: '$8,901.23', type: 'Savings' },
          { name: 'Credit Card', balance: '-$567.89', type: 'Credit' },
        ].map((account) => (
          <Card key={account.name}>
            <CardHeader>
              <CardTitle className="text-lg">{account.name}</CardTitle>
              <CardDescription>{account.type}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{account.balance}</div>
            </CardContent>
          </Card>
        ))}
      </div>
    </motion.div>
  )
}