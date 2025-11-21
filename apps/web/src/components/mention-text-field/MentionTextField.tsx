'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Paper from '@mui/material/Paper';
import Popover from '@mui/material/Popover';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { alpha, useTheme } from '@mui/material/styles';

export interface MentionResource {
  id: string;
  name: string;
  type?: string;
  provider?: string;
  img_src?: string;
}

interface MentionTextFieldProps {
  value: string;
  onChange: (content: string) => void;
  onSearch: (query: string) => Promise<MentionResource[]>;
  onResourceSelect?: (resource: MentionResource) => void;
  getImageUrl?: (resource: MentionResource) => string | undefined;
  existingResources?: MentionResource[];
  placeholder?: string;
}

export default function MentionTextField({
  value,
  onChange,
  onSearch,
  onResourceSelect,
  getImageUrl,
  existingResources = [],
  placeholder,
}: MentionTextFieldProps) {
  const theme = useTheme();
  const editorRef = useRef<HTMLDivElement>(null);
  const [searchResults, setSearchResults] = useState<MentionResource[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState<{ top: number; left: number } | null>(
    null
  );
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [clickedMention, setClickedMention] = useState<MentionResource | null>(null);
  const [mentionPopoverAnchor, setMentionPopoverAnchor] = useState<HTMLElement | null>(null);
  const [cursorPosition, setCursorPosition] = useState<number | null>(null);
  const isInsertingRef = useRef(false);
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const getImageUrlForResource = useCallback(
    (resource: MentionResource): string | undefined => {
      if (getImageUrl) {
        const url = getImageUrl(resource);
        if (url) return url;
      }
      return resource.img_src;
    },
    [getImageUrl]
  );

  const formatContent = useCallback(() => {
    if (!editorRef.current) return;

    const text = value || '';
    const mentionRegex = /@(\w+)/g;
    const parts: Array<{ text: string; isMention: boolean; resource?: MentionResource }> = [];
    let lastIndex = 0;
    let match = mentionRegex.exec(text);

    while (match !== null) {
      if (match.index > lastIndex) {
        parts.push({ text: text.slice(lastIndex, match.index), isMention: false });
      }

      const id = match[1];
      const resource = existingResources.find((r) => r.id === id);
      parts.push({
        text: match[0],
        isMention: true,
        resource,
      });
      lastIndex = match.index + match[0].length;
      match = mentionRegex.exec(text);
    }

    if (lastIndex < text.length) {
      parts.push({ text: text.slice(lastIndex), isMention: false });
    }

    if (parts.length === 0) {
      parts.push({ text, isMention: false });
    }

    const fragment = document.createDocumentFragment();

    parts.forEach((part) => {
      if (part.isMention && part.resource) {
        const span = document.createElement('span');
        span.textContent = part.text;
        span.setAttribute('data-id', part.resource.id || '');
        span.setAttribute('data-name', part.resource.name);
        span.style.cssText = `
          color: ${theme.palette.primary.main};
          background-color: ${alpha(theme.palette.primary.main, 0.1)};
          padding: 2px 4px;
          border-radius: 4px;
          cursor: pointer;
          font-weight: 500;
        `;
        span.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          setClickedMention(part.resource!);
          setMentionPopoverAnchor(span);
        });
        fragment.appendChild(span);
      } else {
        fragment.appendChild(document.createTextNode(part.text));
      }
    });

    editorRef.current.innerHTML = '';
    editorRef.current.appendChild(fragment);

    if (cursorPosition !== null) {
      const walker = document.createTreeWalker(editorRef.current, NodeFilter.SHOW_TEXT, null);
      let currentOffset = 0;
      let node = walker.nextNode();

      while (node) {
        const nodeLength = node.textContent?.length || 0;
        if (currentOffset + nodeLength >= cursorPosition) {
          const range = document.createRange();
          range.setStart(node, Math.min(cursorPosition - currentOffset, nodeLength));
          range.collapse(true);
          const selection = window.getSelection();
          selection?.removeAllRanges();
          selection?.addRange(range);
          break;
        }
        currentOffset += nodeLength;
        node = walker.nextNode();
      }
      setCursorPosition(null);
    }
  }, [value, existingResources, theme, cursorPosition]);

  useEffect(() => {
    if (isInsertingRef.current) {
      formatContent();
      isInsertingRef.current = false;
    }
  }, [formatContent]);

  useEffect(() => {
    if (!editorRef.current || isInsertingRef.current) return;

    const currentText = editorRef.current.textContent || '';
    const isFocused = document.activeElement === editorRef.current;
    if (isFocused) return;

    if (currentText !== value) {
      formatContent();
    }
  }, [value, formatContent]);

  const handleInput = useCallback(
    async (e: React.FormEvent<HTMLDivElement>) => {
      const text = e.currentTarget.textContent || '';
      onChange(text);

      const selection = window.getSelection();
      if (!selection || selection.rangeCount === 0 || !editorRef.current) {
        setShowDropdown(false);
        return;
      }

      const range = selection.getRangeAt(0);
      const rangeClone = range.cloneRange();
      rangeClone.selectNodeContents(editorRef.current);
      rangeClone.setEnd(range.endContainer, range.endOffset);
      const textBeforeCursor = rangeClone.toString();

      const lastAtIndex = textBeforeCursor.lastIndexOf('@');
      if (lastAtIndex !== -1) {
        const afterAt = textBeforeCursor.slice(lastAtIndex + 1);
        if (afterAt.length > 0 && !afterAt.match(/[\s\n\t]/)) {
          const queryMatch = afterAt.match(/^(\w+)$/);

          if (queryMatch && queryMatch[1].length > 0) {
            const query = queryMatch[1];
            
            // Clear existing timeout
            if (searchTimeoutRef.current) {
              clearTimeout(searchTimeoutRef.current);
            }
            
            // Debounce search - wait 300ms after user stops typing
            searchTimeoutRef.current = setTimeout(async () => {
            try {
              const results = await onSearch(query);
              if (results && results.length > 0) {
                setSearchResults(results);
                setSelectedIndex(0);

                const range = selection.getRangeAt(0);
                const rangeClone = range.cloneRange();
                rangeClone.collapse(false);
                const rect = rangeClone.getBoundingClientRect();
                  const editorRect = editorRef.current!.getBoundingClientRect();

                setDropdownPosition({
                    top: rect.bottom - editorRect.top + editorRef.current!.scrollTop + 4,
                    left: rect.left - editorRect.left + editorRef.current!.scrollLeft,
                });
                setShowDropdown(true);
              }
            } catch (error) {
              // Ignore search errors
            }
            }, 300);
            return;
          }
        }
      }

      setShowDropdown(false);
      setDropdownPosition(null);
    },
    [onChange, onSearch]
  );

  const insertMention = useCallback(
    (resource: MentionResource) => {
      if (!editorRef.current) return;

      const fullText = editorRef.current.textContent || '';
      const selection = window.getSelection();
      if (!selection || selection.rangeCount === 0) return;

      const range = selection.getRangeAt(0);

      // Get cursor position in the full text
      let cursorPosition = 0;
      const walker = document.createTreeWalker(editorRef.current, NodeFilter.SHOW_TEXT, null);
      let node = walker.nextNode();

      while (node) {
        if (node === range.startContainer) {
          cursorPosition += range.startOffset;
          break;
        }
        cursorPosition += node.textContent?.length || 0;
        node = walker.nextNode();
      }

      // Find the @ before cursor
      const textBeforeCursor = fullText.slice(0, cursorPosition);
      const lastAtIndex = textBeforeCursor.lastIndexOf('@');
      if (lastAtIndex === -1) return;

      const mentionText = `@${resource.id || resource.name}`;
      const beforeAt = fullText.slice(0, lastAtIndex);
      const afterCursor = fullText.slice(cursorPosition);
      const newText = `${beforeAt}${mentionText} ${afterCursor}`;

      setCursorPosition(lastAtIndex + mentionText.length + 1);
      onChange(newText);
      setShowDropdown(false);
      setDropdownPosition(null);
      onResourceSelect?.(resource);

      isInsertingRef.current = true;
    },
    [onChange, onResourceSelect]
  );

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, []);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLDivElement>) => {
      // Handle Enter key to insert newline character instead of <div>/<br>
      if (e.key === 'Enter' && !showDropdown) {
        e.preventDefault();
        const selection = window.getSelection();
        if (selection && selection.rangeCount > 0) {
          const range = selection.getRangeAt(0);
          range.deleteContents();
          const textNode = document.createTextNode('\n');
          range.insertNode(textNode);
          range.setStartAfter(textNode);
          range.collapse(true);
          selection.removeAllRanges();
          selection.addRange(range);

          // Trigger input event to update value
          if (editorRef.current) {
            const event = new Event('input', { bubbles: true });
            editorRef.current.dispatchEvent(event);
          }
        }
        return;
      }

      if (showDropdown && searchResults.length > 0) {
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          setSelectedIndex((prev) => Math.min(prev + 1, searchResults.length - 1));
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          setSelectedIndex((prev) => Math.max(prev - 1, 0));
        } else if (e.key === 'Enter') {
          e.preventDefault();
          const selected = searchResults[selectedIndex];
          if (selected) {
            insertMention(selected);
          }
        } else if (e.key === 'Escape') {
          e.preventDefault();
          setShowDropdown(false);
          setDropdownPosition(null);
        }
      }
    },
    [showDropdown, searchResults, selectedIndex, insertMention]
  );

  return (
    <Box sx={{ position: 'relative', width: '100%', height: '100%' }}>
      <Box
        ref={editorRef}
        contentEditable
        onInput={handleInput}
        onKeyDown={handleKeyDown}
        suppressContentEditableWarning
        sx={{
          width: '100%',
          height: '100%',
          minHeight: 200,
          p: 2,
          outline: 'none',
          fontFamily: 'monospace',
          fontSize: '0.875rem',
          lineHeight: 1.6,
          overflow: 'auto',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          '&:empty:before': {
            content: `"${placeholder || ''}"`,
            color: theme.palette.text.disabled,
          },
          '&:focus': {
            outline: `2px solid ${alpha(theme.palette.primary.main, 0.2)}`,
            outlineOffset: -2,
          },
        }}
      />

      {showDropdown && dropdownPosition && (
        <Paper
          elevation={8}
          sx={{
            position: 'absolute',
            top: dropdownPosition.top,
            left: dropdownPosition.left,
            zIndex: 1300,
            minWidth: 280,
            maxWidth: 400,
            maxHeight: 300,
            overflow: 'auto',
            mt: 0.5,
          }}
        >
          <List dense sx={{ p: 0.5 }}>
            {searchResults.map((resource, index) => {
              const imageUrl = getImageUrlForResource(resource);
              return (
                <ListItemButton
                  key={resource.id}
                  selected={index === selectedIndex}
                  onClick={() => insertMention(resource)}
                  sx={{
                    borderRadius: 1,
                    '&.Mui-selected': {
                      bgcolor: 'action.selected',
                    },
                  }}
                >
                  {imageUrl && (
                    <ListItemAvatar sx={{ minWidth: 40 }}>
                      <Avatar
                        src={imageUrl}
                        alt={resource.name}
                        sx={{ width: 32, height: 32 }}
                        imgProps={{ style: { objectFit: 'contain' } }}
                      />
                    </ListItemAvatar>
                  )}
                  <ListItemText
                    primary={resource.name}
                    secondary={resource.id}
                    primaryTypographyProps={{
                      variant: 'body2',
                      fontWeight: 500,
                    }}
                    secondaryTypographyProps={{
                      variant: 'caption',
                      color: 'text.secondary',
                    }}
                  />
                </ListItemButton>
              );
            })}
          </List>
        </Paper>
      )}

      <Popover
        open={Boolean(clickedMention)}
        anchorEl={mentionPopoverAnchor}
        onClose={() => {
          setClickedMention(null);
          setMentionPopoverAnchor(null);
        }}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        transformOrigin={{ vertical: 'top', horizontal: 'left' }}
      >
        {clickedMention && (
          <Box sx={{ p: 2, minWidth: 200 }}>
            <Stack direction="row" spacing={1.5} alignItems="center">
              {getImageUrlForResource(clickedMention) && (
                <Avatar
                  src={getImageUrlForResource(clickedMention)}
                  alt={clickedMention.name}
                  sx={{ width: 32, height: 32 }}
                  imgProps={{ style: { objectFit: 'contain' } }}
                />
              )}
              <Box>
                <Typography variant="body2" fontWeight={600}>
                  {clickedMention.name}
                </Typography>
                {clickedMention.id && (
                  <Typography variant="caption" color="text.secondary">
                    {clickedMention.id}
                  </Typography>
                )}
              </Box>
            </Stack>
          </Box>
        )}
      </Popover>
    </Box>
  );
}

