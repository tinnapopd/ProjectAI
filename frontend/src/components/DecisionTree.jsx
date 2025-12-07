import { useEffect, useRef, useState } from "react";
import Tree from "react-d3-tree";
import "./DecisionTree.css";

// Player colors for visual distinction - enhanced for Minimax
const PLAYER_COLORS = {
  root: { bg: "#6366f1", border: "#4f46e5", text: "#fff" },
  max: { bg: "#3b82f6", border: "#2563eb", text: "#fff", name: "MAX (You)" },
  min: {
    bg: "#ef4444",
    border: "#dc2626",
    text: "#fff",
    name: "MIN (Opponent)",
  },
  0: { bg: "#3b82f6", border: "#2563eb", text: "#fff", name: "You" },
  1: { bg: "#f59e0b", border: "#d97706", text: "#fff", name: "Opp 1" },
  2: { bg: "#ef4444", border: "#dc2626", text: "#fff", name: "Opp 2" },
  3: { bg: "#8b5cf6", border: "#7c3aed", text: "#fff", name: "Opp 3" },
  leaf: { bg: "#10b981", border: "#059669", text: "#fff" },
  best: { bg: "#10b981", border: "#047857", text: "#fff" },
};

// Time period colors for visual grouping
const PERIOD_COLORS = [
  "#6366f1", // Purple
  "#3b82f6", // Blue
  "#14b8a6", // Teal
  "#f59e0b", // Amber
  "#ef4444", // Red
  "#8b5cf6", // Violet
];

const DecisionTree = ({ treeData, bestMove, timePeriods, timePeriodUnit }) => {
  const [translate, setTranslate] = useState({ x: 0, y: 0 });
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [tooltip, setTooltip] = useState({
    visible: false,
    x: 0,
    y: 0,
    content: null,
  });
  const treeContainerRef = useRef(null);

  useEffect(() => {
    if (treeContainerRef.current) {
      const rect = treeContainerRef.current.getBoundingClientRect();
      setDimensions({ width: rect.width, height: rect.height });
      setTranslate({
        x: rect.width / 2,
        y: 80,
      });
    }
  }, [treeData]);

  // Handle tooltip
  const showTooltip = (event, nodeDatum) => {
    const rect = treeContainerRef.current.getBoundingClientRect();
    setTooltip({
      visible: true,
      x: event.clientX - rect.left + 10,
      y: event.clientY - rect.top - 10,
      content: nodeDatum,
    });
  };

  const hideTooltip = () => {
    setTooltip({ ...tooltip, visible: false });
  };

  // Transform the tree structure to react-d3-tree format
  const transformTreeData = (nodeId, nodesMap, depth = 0) => {
    const node = nodesMap[nodeId];
    if (!node) return null;

    const isLeaf = node.is_leaf || !node.children || node.children.length === 0;
    const isRoot = node.is_root || node.parent_id === null;
    const isBestMove = node.label === bestMove && node.player_index === 0;
    // Explicitly check for true/false, not null/undefined
    const isMaxNode = node.is_max_node === true;
    const isMinNode = node.is_max_node === false && node.is_max_node !== null;
    const timePeriod = node.time_period;

    // Truncate long labels for display
    const truncateLabel = (label, maxLen = 20) => {
      if (!label) return "";
      return label.length > maxLen ? label.substring(0, maxLen) + "..." : label;
    };

    const transformed = {
      name: truncateLabel(node.label),
      fullName: node.label,
      attributes: {
        score: node.score,
        playerIndex: node.player_index,
        isLeaf,
        isRoot,
        isBestMove,
        isMaxNode,
        isMinNode,
        timePeriod,
        depth,
      },
      children: [],
    };

    if (node.children && node.children.length > 0) {
      transformed.children = node.children
        .map((childId) => transformTreeData(childId, nodesMap, depth + 1))
        .filter((child) => child !== null);
    }

    return transformed;
  };

  if (!treeData || Object.keys(treeData).length === 0) {
    return (
      <div className="tree-container">
        <p className="no-data">No decision tree data available</p>
      </div>
    );
  }

  const nodesMap = treeData;
  const rootId =
    Object.keys(nodesMap).find((key) => nodesMap[key].parent_id === null) ||
    "node_0";
  const transformedData = transformTreeData(rootId, nodesMap);

  if (!transformedData) {
    return (
      <div className="tree-container">
        <p className="no-data">Unable to render tree structure</p>
      </div>
    );
  }

  // Get unique players for legend
  const players = new Set();
  Object.values(nodesMap).forEach((node) => {
    if (node.player_index !== null && node.player_index !== undefined) {
      players.add(node.player_index);
    }
  });

  // Custom node rendering
  const renderCustomNode = ({ nodeDatum, toggleNode }) => {
    const {
      isLeaf,
      isRoot,
      isBestMove,
      playerIndex,
      score,
      isMaxNode,
      isMinNode,
      timePeriod,
    } = nodeDatum.attributes || {};

    // Determine colors based on Minimax node type
    let colors;
    if (isBestMove) {
      colors = PLAYER_COLORS.best;
    } else if (isRoot) {
      colors = PLAYER_COLORS.root;
    } else if (isLeaf) {
      colors = PLAYER_COLORS.leaf;
    } else if (isMaxNode) {
      // MAX node - your turn (blue)
      colors = PLAYER_COLORS.max;
    } else if (isMinNode) {
      // MIN node - opponent turn (use opponent color)
      colors = PLAYER_COLORS[playerIndex] || PLAYER_COLORS.min;
    } else {
      colors = PLAYER_COLORS[playerIndex] || PLAYER_COLORS[0];
    }

    // Get period color for border accent
    const periodColor =
      timePeriod !== null && timePeriod >= 0
        ? PERIOD_COLORS[timePeriod % PERIOD_COLORS.length]
        : null;

    // Compact node sizes
    const nodeSize = isLeaf ? 24 : isRoot ? 40 : 36;

    return (
      <g
        onClick={toggleNode}
        onMouseEnter={(e) => showTooltip(e, nodeDatum)}
        onMouseLeave={hideTooltip}
        style={{ cursor: "pointer" }}
      >
        {/* Time period indicator ring */}
        {periodColor && !isRoot && (
          <circle
            r={nodeSize / 2 + 4}
            fill="none"
            stroke={periodColor}
            strokeWidth={2}
            strokeDasharray={isMaxNode ? "none" : "4,2"}
            opacity={0.6}
          />
        )}

        {/* Glow effect for best move */}
        {isBestMove && (
          <circle
            r={nodeSize / 2 + 6}
            fill="#10b981"
            opacity={0.3}
            style={{ filter: "blur(6px)" }}
          />
        )}

        {/* Main node circle */}
        <circle
          r={nodeSize / 2}
          fill={colors.bg}
          stroke={colors.border}
          strokeWidth={isBestMove ? 3 : 2}
          style={{
            filter: `drop-shadow(0 2px 6px ${colors.bg}50)`,
            transition: "all 0.2s ease",
          }}
        />

        {/* MAX/MIN indicator */}
        {!isRoot && !isLeaf && (
          <text
            x={0}
            y={4}
            textAnchor="middle"
            fontSize="10"
            fill={colors.text}
            fontWeight="bold"
            style={{ pointerEvents: "none" }}
          >
            {isMaxNode ? "▲" : "▼"}
          </text>
        )}

        {/* Inner circle for visual depth */}
        <circle
          r={nodeSize / 2 - 4}
          fill="none"
          stroke="rgba(255,255,255,0.2)"
          strokeWidth={1}
        />

        {/* Best move star */}
        {isBestMove && (
          <text
            x={nodeSize / 2 + 8}
            y={-nodeSize / 2 + 4}
            fontSize="14"
            style={{ pointerEvents: "none" }}
          >
            ⭐
          </text>
        )}
      </g>
    );
  };

  // Custom path style
  const getDynamicPathClass = ({ source, target }) => {
    if (target?.data?.attributes?.isBestMove) {
      return "link-best";
    }
    return "link-normal";
  };

  return (
    <div className="tree-container" ref={treeContainerRef}>
      {/* Legend */}
      <div className="tree-legend">
        <div className="legend-title">Minimax Legend</div>

        {/* Best Move - highlighted at top */}
        <div className="legend-item best">
          <span
            className="legend-box"
            style={{
              background: PLAYER_COLORS.best.bg,
              boxShadow: "0 0 8px #10b981",
            }}
          ></span>
          <span>⭐ Best Move</span>
        </div>

        <div className="legend-divider"></div>

        {/* Minimax node types */}
        <div className="legend-item">
          <span
            className="legend-box"
            style={{ background: PLAYER_COLORS.root.bg }}
          ></span>
          <span>Root</span>
        </div>
        <div className="legend-item">
          <span
            className="legend-box"
            style={{ background: PLAYER_COLORS.max.bg }}
          ></span>
          <span>▲ MAX (Your Turn)</span>
        </div>
        <div className="legend-item">
          <span
            className="legend-box"
            style={{ background: PLAYER_COLORS.min.bg }}
          ></span>
          <span>▼ MIN (Opponent)</span>
        </div>
        <div className="legend-item">
          <span
            className="legend-box"
            style={{ background: PLAYER_COLORS.leaf.bg }}
          ></span>
          <span>Outcomes</span>
        </div>

        {/* Time periods legend */}
        {timePeriods > 0 && (
          <>
            <div className="legend-divider"></div>
            <div className="legend-subtitle">Time Periods</div>
            {Array.from({ length: Math.min(timePeriods, 6) }, (_, i) => (
              <div key={i} className="legend-item">
                <span
                  className="legend-box legend-ring"
                  style={{
                    borderColor: PERIOD_COLORS[i % PERIOD_COLORS.length],
                  }}
                ></span>
                <span>
                  {timePeriodUnit
                    ? `${
                        timePeriodUnit.charAt(0).toUpperCase() +
                        timePeriodUnit.slice(1)
                      } ${i + 1}`
                    : `Period ${i + 1}`}
                </span>
              </div>
            ))}
          </>
        )}
      </div>

      {/* Instructions */}
      <div className="tree-instructions">
        <span>
          🖱️ Drag to pan • Scroll to zoom • Hover for details • {timePeriods}{" "}
          {timePeriodUnit}(s) shown
        </span>
      </div>

      {/* Tooltip */}
      {tooltip.visible && tooltip.content && (
        <div
          className="tree-tooltip"
          style={{
            left: tooltip.x,
            top: tooltip.y,
          }}
        >
          <div className="tooltip-header">
            {/* Node type badge */}
            {tooltip.content.attributes?.isRoot && (
              <span className="tooltip-badge root">Root</span>
            )}
            {tooltip.content.attributes?.isLeaf && (
              <span className="tooltip-badge leaf">Final Outcome</span>
            )}
            {!tooltip.content.attributes?.isRoot &&
              !tooltip.content.attributes?.isLeaf && (
                <>
                  {tooltip.content.attributes?.isMaxNode && (
                    <span className="tooltip-badge max">▲ MAX (Your Turn)</span>
                  )}
                  {tooltip.content.attributes?.isMinNode && (
                    <span
                      className="tooltip-badge"
                      style={{
                        background:
                          PLAYER_COLORS[tooltip.content.attributes.playerIndex]
                            ?.bg || PLAYER_COLORS.min.bg,
                      }}
                    >
                      ▼ MIN (Opponent {tooltip.content.attributes.playerIndex})
                    </span>
                  )}
                </>
              )}

            {/* Best Move badge */}
            {tooltip.content.attributes?.isBestMove && (
              <span className="tooltip-badge best">⭐ Best Move</span>
            )}
          </div>

          {/* Time period indicator */}
          {tooltip.content.attributes?.timePeriod !== null &&
            tooltip.content.attributes?.timePeriod !== undefined &&
            tooltip.content.attributes?.timePeriod >= 0 && (
              <div
                className="tooltip-period"
                style={{
                  borderLeft: `3px solid ${
                    PERIOD_COLORS[
                      tooltip.content.attributes.timePeriod %
                        PERIOD_COLORS.length
                    ]
                  }`,
                }}
              >
                {timePeriodUnit
                  ? `${
                      timePeriodUnit.charAt(0).toUpperCase() +
                      timePeriodUnit.slice(1)
                    } ${tooltip.content.attributes.timePeriod + 1}`
                  : `Period ${tooltip.content.attributes.timePeriod + 1}`}
              </div>
            )}

          {/* Show label */}
          {tooltip.content.attributes?.isRoot ? (
            <div className="tooltip-label">
              <span style={{ opacity: 0.7, fontSize: "11px" }}>Game Tree:</span>
              <br />
              {tooltip.content.fullName}
            </div>
          ) : (
            <div className="tooltip-label">{tooltip.content.fullName}</div>
          )}

          {tooltip.content.attributes?.score !== null &&
            tooltip.content.attributes?.score !== undefined && (
              <div className="tooltip-score">
                Minimax Score:{" "}
                <strong>{tooltip.content.attributes.score.toFixed(3)}</strong>
              </div>
            )}
        </div>
      )}

      <Tree
        data={transformedData}
        translate={translate}
        dimensions={dimensions}
        orientation="vertical"
        pathFunc="step"
        renderCustomNodeElement={renderCustomNode}
        pathClassFunc={getDynamicPathClass}
        separation={{ siblings: 1, nonSiblings: 1.2 }}
        nodeSize={{ x: 80, y: 80 }}
        zoom={0.85}
        scaleExtent={{ min: 0.3, max: 3 }}
        enableLegacyTransitions={true}
        transitionDuration={300}
        depthFactor={80}
        shouldCollapseNeighborNodes={false}
        initialDepth={10}
      />
    </div>
  );
};

export default DecisionTree;
