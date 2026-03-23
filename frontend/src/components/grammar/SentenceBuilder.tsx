'use client'
import { useState } from 'react'
import { DndContext, closestCenter, DragEndEvent, DragStartEvent, DragOverlay, PointerSensor, useSensor, useSensors } from '@dnd-kit/core'
import { SortableContext, horizontalListSortingStrategy, useSortable, arrayMove } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { motion, AnimatePresence } from 'framer-motion'

interface Props {
  words: string[]
  onAnswer: (answer: string) => void
  disabled?: boolean
  result?: 'correct' | 'wrong' | null
}

function SortableChip({ id, word, onRemove, disabled, isResult }: { id: string, word: string, onRemove: () => void, disabled?: boolean, isResult?: 'correct'|'wrong'|null }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id, disabled })
  const bg = isResult === 'correct' ? '#166534' : isResult === 'wrong' ? '#7f1d1d' : '#1e3a5f'
  const fg = isResult === 'correct' ? '#86efac' : isResult === 'wrong' ? '#fca5a5' : '#93c5fd'

  return (
    <div ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition, opacity: isDragging ? 0.4 : 1 }}
      className="relative group"
      {...attributes} {...listeners}>
      <div className="px-4 py-2 rounded-xl font-bold text-base cursor-grab active:cursor-grabbing select-none hanzi transition-colors"
        style={{ background: bg, color: fg, border: `1px solid ${isResult ? 'transparent' : '#2a4a80'}` }}>
        {word}
      </div>
      {!disabled && !isResult && (
        <button onClick={e => { e.stopPropagation(); onRemove() }}
          className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full text-xs opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
          style={{ background: '#ef4444', color: 'white' }}>
          ×
        </button>
      )}
    </div>
  )
}

export function SentenceBuilder({ words: initialWords, onAnswer, disabled, result }: Props) {
  const [source, setSource] = useState<string[]>(initialWords)
  const [answer, setAnswer] = useState<string[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }))

  function addWord(word: string) {
    const idx = source.indexOf(word)
    if (idx === -1) return
    setSource(s => s.filter((_, i) => i !== idx))
    setAnswer(a => [...a, word])
  }

  function removeWord(idx: number) {
    const word = answer[idx]
    setAnswer(a => a.filter((_, i) => i !== idx))
    setSource(s => [...s, word])
  }

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event
    setActiveId(null)
    if (!over || active.id === over.id) return
    const oldIdx = answer.findIndex(w => `ans-${w}-${answer.indexOf(w)}` === active.id)
    const newIdx = answer.findIndex(w => `ans-${w}-${answer.indexOf(w)}` === over.id)
    if (oldIdx !== -1 && newIdx !== -1) {
      setAnswer(a => arrayMove(a, oldIdx, newIdx))
    }
  }

  const answerIds = answer.map((w, i) => `ans-${w}-${i}`)

  return (
    <div className="space-y-4">
      {/* Answer zone */}
      <div>
        <p className="text-xs mb-2 font-semibold" style={{ color: 'var(--text-muted)' }}>YOUR ANSWER</p>
        <div className="min-h-[60px] rounded-xl p-3 flex flex-wrap gap-2 items-center"
          style={{ background: '#0d1526', border: '1.5px solid', borderColor: result === 'correct' ? '#22c55e' : result === 'wrong' ? '#ef4444' : '#1e3a5f' }}>
          {answer.length === 0 ? (
            <span className="text-sm italic" style={{ color: '#334155' }}>Click words below · drag to reorder</span>
          ) : (
            <DndContext sensors={sensors} collisionDetection={closestCenter}
              onDragStart={e => setActiveId(e.active.id as string)}
              onDragEnd={handleDragEnd}>
              <SortableContext items={answerIds} strategy={horizontalListSortingStrategy}>
                {answer.map((word, i) => (
                  <SortableChip key={answerIds[i]} id={answerIds[i]} word={word}
                    onRemove={() => removeWord(i)} disabled={disabled} isResult={result} />
                ))}
              </SortableContext>
              <DragOverlay>
                {activeId && (
                  <div className="px-4 py-2 rounded-xl font-bold hanzi"
                    style={{ background: '#f59e0b', color: '#000', opacity: 0.9 }}>
                    {answer[answerIds.indexOf(activeId)]}
                  </div>
                )}
              </DragOverlay>
            </DndContext>
          )}
        </div>
      </div>

      {/* Source words */}
      {source.length > 0 && (
        <div>
          <p className="text-xs mb-2 font-semibold" style={{ color: 'var(--text-muted)' }}>ARRANGE:</p>
          <div className="flex flex-wrap gap-2">
            <AnimatePresence>
              {source.map((word, i) => (
                <motion.button key={`src-${word}-${i}`}
                  initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  onClick={() => !disabled && addWord(word)}
                  disabled={disabled}
                  className="px-4 py-2 rounded-xl font-bold text-base hanzi transition-colors hover:opacity-80 active:scale-95"
                  style={{ background: '#2563eb', color: '#fff', cursor: disabled ? 'default' : 'pointer' }}>
                  {word}
                </motion.button>
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}

      {/* Check button */}
      {!disabled && answer.length > 0 && (
        <button onClick={() => onAnswer(answer.join(''))}
          className="btn-success w-full py-3 mt-2">
          ✔  Check
        </button>
      )}
    </div>
  )
}
