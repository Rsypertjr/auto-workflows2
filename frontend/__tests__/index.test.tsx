// frontend/__tests__/index.test.tsx 
import { render, screen } from '@testing-library/react'
import Home from '../../frontend/src/app/page.tsx'
import '@testing-library/jest-dom'
import { describe, it, expect } from 'vitest'

describe('Automated Homepage Render Test', () => {
    it('renders the system dashboard heading without crashing', () => {
        render(<Home />)
        const heading = screen.getByRole('heading', {
            name: /production dashboard/i,
        })

        expect(heading).toBeInTheDocument()
    })
})